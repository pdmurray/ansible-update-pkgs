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

def section_ubuntu_nodes():
    return get_input_list("Enter an ubuntu node (or press Enter to finish): ")

def section_pihole_nodes():
    nodes_info = []
    while True:
        node = input("Enter a pihole node (or press Enter to finish): ")
        if not node:
            break
        ansible_user = input(f"Enter ansible_user for {node}: ")
        nodes_info.append((node, ansible_user))
    return nodes_info

def create_ansible_content():
    sections = {
        "ansible_become_password": input("Enter ansible_become_password: "),
        "ubuntu_nodes": section_ubuntu_nodes(),
        "ubuntu_nodes_vars": None,
        "pihole_nodes": section_pihole_nodes()
    }
    if sections["ubuntu_nodes"]:
        sections["ubuntu_nodes_vars"] = input("Enter common ansible_user for all ubuntu nodes: ")

    return sections

def section_servers():
    servers_info = []
    while True:
        hostname = input("Enter a truenas server hostname (or press Enter to finish): ")
        if not hostname:
            break
        token = input(f"Enter token for {hostname}: ")
        servers_info.append((hostname, token))
    return servers_info

def create_truenas_content():
    return {"servers": section_servers()}

def render_ansible_content(sections):
    content = f"[all:vars]\nansible_become_password={sections['ansible_become_password']}\n\n"
    content += "[ubuntu_nodes]\n" + "\n".join(sections["ubuntu_nodes"]) + "\n"
    if sections["ubuntu_nodes_vars"]:
        content += f"\n[ubuntu_nodes:vars]\nansible_user={sections['ubuntu_nodes_vars']}\n"
    content += "\n[pihole_nodes]\n" + "\n".join([f"{node} ansible_user={user}" for node, user in sections["pihole_nodes"]])

    return content

def render_truenas_content(sections):
    return "servers:\n" + "\n".join([f"  - hostname: {hostname}\n    token: {token}\n    validate_certs: false" for hostname, token in sections["servers"]])

def preview_and_edit(content_creator, content_renderer):
    sections = content_creator()
    
    section_names = list(sections.keys())

    while True:
        content = content_renderer(sections)
        print("\n" + "-" * 40 + "\n")
        print(content)
        print("\n" + "-" * 40 + "\n")
        
        print("Sections available for editing:")
        for idx, section in enumerate(section_names, 1):
            print(f"{idx}. {section}")
        
        try:
            decision_idx = int(input("Which section would you like to edit? (Enter section number or '0' to finish): "))
            if decision_idx == 0:
                break
            if 0 < decision_idx <= len(section_names):
                decision = section_names[decision_idx-1]
            else:
                print("Invalid choice. Please choose again.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if decision == "ansible_become_password":
            sections[decision] = input("Enter ansible_become_password: ")
        elif decision == "ubuntu_nodes":
            sections[decision] = section_ubuntu_nodes()
        elif decision == "ubuntu_nodes_vars":
            sections[decision] = input("Enter common ansible_user for all ubuntu nodes: ")
        elif decision == "pihole_nodes":
            sections[decision] = section_pihole_nodes()
        elif decision == "servers":
            sections[decision] = section_servers()

    return content

def main():
    ansible_content = preview_and_edit(create_ansible_content, render_ansible_content)
    ansible_filename = input("Enter the filename for the ansible inventory (default: inventory.ini): ") or "inventory.ini"
    with open(ansible_filename, "w") as f:
        f.write(ansible_content)
    os.chmod(ansible_filename, 0o600)

    truenas_content = preview_and_edit(create_truenas_content, render_truenas_content)
    truenas_filename = input("Enter the filename for the truenas servers (default: truenas-servers.yml): ") or "truenas-servers.yml"
    with open(truenas_filename, "w") as f:
        f.write(truenas_content)
    os.chmod(truenas_filename, 0o600)

if __name__ == "__main__":
    main()
