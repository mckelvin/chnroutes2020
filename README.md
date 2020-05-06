# CHNROUTES2020

This is a WIP replica of [fivesheep/chnroutes](https://github.com/fivesheep/chnroutes).

```
$ pip install git+https://github.com/mckelvin/chnroutes2020#egg=chnroutes2020

$ chnroutes2020 --help
Usage: chnroutes2020 [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  Enable debug log
  --help                Show this message and exit.

Commands:
  check     Check if a hostname or an IPv4 address is in the local list.
  generate  Generate route command for target.

$ chnroutes2020 generate surge | head
IP-CIDR,1.0.1.0/24,DIRECT
IP-CIDR,1.0.2.0/23,DIRECT
IP-CIDR,1.0.8.0/21,DIRECT
IP-CIDR,1.0.32.0/19,DIRECT
IP-CIDR,1.1.0.0/24,DIRECT
IP-CIDR,1.1.2.0/23,DIRECT
IP-CIDR,1.1.4.0/22,DIRECT
IP-CIDR,1.1.8.0/24,DIRECT
IP-CIDR,1.1.9.0/24,DIRECT
IP-CIDR,1.1.10.0/23,DIRECT

$ chnroutes2020 generate macos_setup | head
sudo route -n add -net 1.0.1.0/24 192.168.1.1
sudo route -n add -net 1.0.2.0/23 192.168.1.1
sudo route -n add -net 1.0.8.0/21 192.168.1.1
sudo route -n add -net 1.0.32.0/19 192.168.1.1
sudo route -n add -net 1.1.0.0/24 192.168.1.1
sudo route -n add -net 1.1.2.0/23 192.168.1.1
sudo route -n add -net 1.1.4.0/22 192.168.1.1
sudo route -n add -net 1.1.8.0/24 192.168.1.1
sudo route -n add -net 1.1.9.0/24 192.168.1.1
sudo route -n add -net 1.1.10.0/23 192.168.1.1

$ chnroutes2020 generate macos_teardown | head
sudo route -n delete -net 1.0.1.0/24 192.168.1.1
sudo route -n delete -net 1.0.2.0/23 192.168.1.1
sudo route -n delete -net 1.0.8.0/21 192.168.1.1
sudo route -n delete -net 1.0.32.0/19 192.168.1.1
sudo route -n delete -net 1.1.0.0/24 192.168.1.1
sudo route -n delete -net 1.1.2.0/23 192.168.1.1
sudo route -n delete -net 1.1.4.0/22 192.168.1.1
sudo route -n delete -net 1.1.8.0/24 192.168.1.1
sudo route -n delete -net 1.1.9.0/24 192.168.1.1
sudo route -n delete -net 1.1.10.0/23 192.168.1.1

$ chnroutes2020 check 8.8.8.8
INFO:chnroutes2020.__main__:Record not found for 8.8.8.8

$ chnroutes2020 check t.cn
INFO:chnroutes2020.__main__:Record found for t.cn(116.211.169.137) in 116.208.0.0/14
```
