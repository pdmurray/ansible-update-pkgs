#!/bin/bash
TRUENAS_CONFIG_FILE=./truenas-servers.yml ansible-playbook -i inventory.ini update-truenas-charts.yml
