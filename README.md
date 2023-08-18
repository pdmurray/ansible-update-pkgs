# ansible-update-pkgs

A simple ansible project to keep my servers / pihole nodes updated.


## Pre-Reqs:

 - ansible (`pipx install --include-deps ansible`)
 - jmespath (`python3 -m pip install jmespath`)


Set up a truenas-servers.yml file in the root with the following structure:

```
servers:
  - hostname: my-server.mydomain.com
    token: xxxxxxxxxxx
    validate_certs: false
```

In addition, create an inventory.ini file with the following structure:

```
[ubuntu_nodes]
host1
host2
host3

[pihole_nodes]
host4 ansible_user=root
host5 ansible_user=pi
```