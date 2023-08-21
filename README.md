# ansible-update-pkgs

A simple ansible project to keep my servers / pihole nodes updated.


## Pre-Reqs:

 - ansible (`pipx install --include-deps ansible`)
 - jmespath (`python3 -m pip install jmespath`)
 - Helm (https://helm.sh/docs/intro/install/)

Set up a truenas-servers.yml file in the root with the following structure:

```
servers:
  - hostname: my-server.mydomain.com
    token: xxxxxxxxxxx
    validate_certs: false
```

In addition, create an inventory.ini file with the following structure:

```
[all:vars]
ansible_become_password=**********

[ubuntu_nodes]
node1
node2
node3

[ubuntu_nodes:vars]
ansible_user=pdmurray

[pihole_nodes]
node4 ansible_user=root
node5 ansible_user=pi

```

## Usage

### Running locally

```
# Update packages on ubuntu_nodes, and if necessary, reboot the nodes
$ ansible-playbook -i inventory.ini update-packages.yml --ask-become-pass

# Update packages and pihole itself on pihole_nodes
$ ansible-playbook -i inventory.ini update-pihole.yml --ask-become-pass

# Reboot nodes
$ ansible-playbook -i inventory.ini reboot-nodes.yml --ask-become-pass

# Update TrueNAS SCALE installed Helm Charts
$ ansible-playbook update-truenas-charts.yml
```

### Running on Kubernetes

To use with kubernetes, create the necessary secrets:

```
$ kubectl create secret generic inventory-secret --from-file=inventory.ini=./inventory.ini

$ kubectl create secret generic ssh-key-secret --from-file=id_rsa=./id_rsa

```

Then, deploy the cronjob:

```
$ kubectl apply -f cronjob.yaml
```

### Running with Helm

Fill in the values file with the inventory and ssh key in the appropropriate fields, then:

```
helm install ansible-job ./ansible-job-chart
```