#!/usr/bin/python3

import os
import sys
import json
import math
import socket
import logging
import tempfile
import ipaddress
import subprocess

import click
import requests


logger = logging.getLogger(__name__)


class ChnRoutes2020:

    DELEGATED_APNIC_LATEST_URL = \
        "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"
    CN_IPV4_PREFIX = "apnic|CN|ipv4|"

    TMPL_DICT = {
        "surge": "IP-CIDR,{starting_ip}/{num_mask},DIRECT",
        "macos_setup": "sudo route -n add -net {starting_ip}/{num_mask} {default_gateway}",
        "macos_teardown": "sudo route -n delete -net {starting_ip}/{num_mask} {default_gateway}",
        "windows_setup": "route add {starting_ip} mask {ip_mask} {default_gateway} metric 5",
        "windows_teardown": "route delete {starting_ip}",
        "default": "{starting_ip}/{num_mask}",
    }

    def __init__(self):
        self.work_dir = os.path.join(tempfile.gettempdir(), "chnroutes2020")
        logger.debug("Work dir: %s", self.work_dir)
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

        self.cached_file = os.path.join(
            self.work_dir,
            "delegated-apnic-latest",
        )
        self.cached_meta_file = os.path.join(
            self.work_dir,
            ".delegated-apnic-latest.json",
        )
        try:
            self.default_gw = self.get_default_gateway()
        except Exception:
            logging.exception("Failed to find default gateway")
            if os.name == "posix":
                self.default_gw = "$DEFAULT_ROUTE"
            else:
                self.default_gw = "%gw%"

    def download_delegated_apnic_file(self, url=None):
        if url is None:
            url = self.DELEGATED_APNIC_LATEST_URL

        etag = None
        if os.path.exists(self.cached_meta_file):
            with open(self.cached_meta_file) as fhandler:
                metadata = json.load(fhandler)
                etag = metadata["ETag"]

        head_rsp = requests.head(url)
        if etag == head_rsp.headers["ETag"]:
            logger.debug(
                "Remote file unchanged, using local copy %s",
                self.cached_file
            )
            return

        response = requests.get(url)
        assert response.status_code == 200, response

        with open(self.cached_file, "wb") as fhandler:
            fhandler.write(response.content)

        with open(self.cached_meta_file, "w") as fhandler:
            json.dump(dict(head_rsp.headers), fhandler)

        logger.debug("File downloaded at %s", self.cached_file)

    def _process_line(self, line):
        if not line.startswith(self.CN_IPV4_PREFIX):
            return

        # apnic|CN|ipv4|223.252.128.0|32768|20110131|allocated<Paste>
        cols = line.strip().split("|")
        starting_ip = cols[3]
        ip_num = int(cols[4])
        num_mask = 32 - int(math.log2(ip_num))
        ip_mask = str(ipaddress.IPv4Address(0xFFFFFFFF ^ (ip_num - 1)))

        return {
            "starting_ip": starting_ip,
            "num_mask": num_mask,
            "ip_mask": ip_mask,
            "default_gateway": self.default_gw,
        }

    def _yield_cn_ipv4_records(self):
        if not os.path.exists(self.cached_file):
            raise RuntimeError(
                f"{self.cached_file} not found. Please download the file "
                f"by running the generate command first."
            )
        with open(self.cached_file, "r") as fhandler:
            for line in fhandler:
                ip_range_dct = self._process_line(line)
                if ip_range_dct is not None:
                    yield ip_range_dct

    def generate(self, target=None):
        tmpl = self.TMPL_DICT.get(target)
        if tmpl is None:
            tmpl = self.TMPL_DICT["default"]

        for ip_range_dct in self._yield_cn_ipv4_records():
            print(tmpl.format(**ip_range_dct))

    def get_default_gateway(self):
        """
        WIP
        """
        if sys.platform != "darwin":
            raise NotImplementedError(
                "Default route unknown for {sys.platform}"
            )
        lines = subprocess.check_output(["netstat", "-nr"]).splitlines()
        option_dict = {}
        for line in lines:
            line = line.decode("utf-8")
            if not line.startswith("default"):
                continue

            cols = line.split()
            gw_ip = cols[1]
            gw_name = cols[3]
            option_dict[gw_name] = gw_ip

        for gw_name in ["en4", "en0"]:
            if gw_name in option_dict:
                return option_dict[gw_name]

        raise RuntimeError("Gateway not found")

    def find_record_by_ip(self, hostname_or_ip):
        target_ip = ipaddress.IPv4Address(socket.gethostbyname(hostname_or_ip))
        for ip_range_dct in self._yield_cn_ipv4_records():
            starting_ip = ipaddress.IPv4Address(ip_range_dct["starting_ip"])
            ip_mask = ipaddress.IPv4Address(ip_range_dct["ip_mask"])
            if int(target_ip) & int(ip_mask) == int(starting_ip):
                return str(target_ip), ip_range_dct
        return None


@click.group()
@click.option("--debug/--no-debug", default=False,
              help='Enable debug log')
@click.pass_context
def cli(ctx, debug):
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)
    ctx.ensure_object(dict)
    ctx.obj["app"] = ChnRoutes2020()


@cli.command("check")
@click.pass_context
@click.argument('hostname', nargs=1)
def check_ip(ctx, hostname):
    """
    Check if a hostname or an IPv4 address is in the local list.
    """
    app = ctx.obj["app"]
    rst = app.find_record_by_ip(hostname)
    if rst is None:
        logger.info("Record not found for %s", hostname)
    else:
        target_ip, ip_range_dct = rst
        if target_ip != hostname:
            hostname_str = f"{hostname}({target_ip})"
        else:
            hostname_str = hostname
        logger.info(
            "Record found for %s in %s/%s",
            hostname_str,
            ip_range_dct["starting_ip"],
            ip_range_dct["num_mask"],
        )


@cli.command("generate")
@click.pass_context
@click.argument('target', nargs=1)
def generate_rules(ctx, target):
    """
    Generate route command for target.
    Target is any of
    surge,
    macos_setup, macos_teardown,
    windows_setup, windows_teardown,
    default
    """
    app = ctx.obj["app"]
    if target is not None and "teardown" not in target:
        app.download_delegated_apnic_file()
    else:
        logger.debug(
            "This is a 'teardown' target, "
            "I'm not going to download the file."
        )
    app.generate(target)


if __name__ == "__main__":
    cli()
