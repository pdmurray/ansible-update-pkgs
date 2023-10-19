#!/bin/bash
ansible-playbook -i inventory.ini update-packages.yml --ask-become-pass
