#!/bin/bash
ansible-playbook -i inventory.ini update-pihole.yml --ask-become-pass
