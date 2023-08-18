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

## Usage

```
# Update packages on ubuntu_nodes, and if necessary, reboot the nodes
$ ansible-playbook -i inventory.ini update-packages.yml

# Update packages and pihole itself on pihole_nodes
$ ansible-playbook -i inventory.ini update-pihole.yml

# Reboot nodes
$ ansible-playbook -i inventory.ini reboot-nodes.yml

# Update TrueNAS SCALE installed Helm Charts
$ ansible-playbook update-truenas-charts.yml
```