#!/usr/bin/env python3
import os

def get_input_list(prompt):
    nodes = []
    while True:
        node = input(prompt)
        if not node:
            break
        nodes.append(node)
    return nodes

def create_ansible_file():
    ansible_become_password = input("Enter ansible_become_password: ")

    ubuntu_nodes = get_input_list("Enter an ubuntu node (or press Enter to finish): ")

    pihole_nodes_info = []
    while True:
        node = input("Enter a pihole node (or press Enter to finish): ")
        if not node:
            break
        ansible_user = input(f"Enter ansible_user for {node}: ")
        pihole_nodes_info.append((node, ansible_user))

    with open("inventory.ini", "w") as f:
        f.write("[all:vars]\n")
        f.write(f"ansible_become_password={ansible_become_password}\n\n")
        f.write("[ubuntu_nodes]\n")
        for node in ubuntu_nodes:
            f.write(node + "\n")
        f.write("\n[ubuntu_nodes:vars]\n")
        if ubuntu_nodes:
            ansible_user_ubuntu = input("Enter common ansible_user for all ubuntu nodes: ")
            f.write(f"ansible_user={ansible_user_ubuntu}\n")
        f.write("\n[pihole_nodes]\n")
        for node, ansible_user in pihole_nodes_info:
            f.write(f"{node} ansible_user={ansible_user}\n")

    os.chmod("inventory.ini", 0o600)

def create_truenas_file():
    servers_info = []
    while True:
        hostname = input("Enter a truenas server hostname (or press Enter to finish): ")
        if not hostname:
            break
        token = input(f"Enter token for {hostname}: ")
        servers_info.append((hostname, token))

    with open("truenas-servers.yml", "w") as f:
        f.write("servers:\n")
        for hostname, token in servers_info:
            f.write(f"  - hostname: {hostname}\n")
            f.write(f"    token: {token}\n")
            f.write("    validate_certs: false\n")

    os.chmod("truenas-servers.yml", 0o600)

def main():
    create_ansible_file()
    create_truenas_file()

if __name__ == "__main__":
    main()

