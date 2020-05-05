# CHNROUTES2020

This is a WIP replica of [fivesheep/chnroutes](https://github.com/fivesheep/chnroutes).

```
$ python chnroute2020/__main__.py --help
Usage: __main__.py [OPTIONS]

Options:
  -t, --target TEXT  Any of surge macos_setup macos_teardown windows_setup
                     windows_teardown default
  -c, --check TEXT   Check if the target ip is listed
  --help             Show this message and exit.

$ python chnroute2020/__main__.py -t surge | head
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

$ python chnroute2020/__main__.py -t macos_setup | head
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

$ python chnroute2020/__main__.py -t macos_teardown | head
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

$ python chnroute2020/__main__.py -c 114.114.114.114
INFO:__main__:Record found for 114.114.114.114 in 114.112.0.0/14

$ python chnroute2020/__main__.py -c 8.8.8.8
INFO:__main__:Record not found for 8.8.8.8
```
