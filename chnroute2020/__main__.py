#!/usr/bin/python3

import os
import sys
import json
import math
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

    def find_record_by_ip(self, target_ip):
        for ip_range_dct in self._yield_cn_ipv4_records():
            starting_ip = ipaddress.IPv4Address(ip_range_dct["starting_ip"])
            ip_mask = ipaddress.IPv4Address(ip_range_dct["ip_mask"])
            target_ip = ipaddress.IPv4Address(target_ip)
            if int(target_ip) & int(ip_mask) == int(starting_ip):
                return ip_range_dct
        return None


@click.command()
@click.option("-t", "--target",
              help='Any of %s' % " ".join(ChnRoutes2020.TMPL_DICT.keys()))
@click.option("-c", "--check",
              help='Check if the target ip is listed')
def cli(target, check):
    logging.basicConfig(level=logging.INFO)
    app = ChnRoutes2020()
    if check is not None:
        rst = app.find_record_by_ip(check)
        if rst is None:
            logger.info("Record not found for %s", check)
        else:
            logger.info(
                "Record found for %s in %s/%s",
                check,
                rst["starting_ip"],
                rst["num_mask"],
            )
    else:
        if target is not None and "teardown" not in target:
            logger.debug("Use existing file for teardown")
            app.download_delegated_apnic_file()
        app.generate(target)


if __name__ == "__main__":
    cli()
