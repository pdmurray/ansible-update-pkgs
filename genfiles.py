#!/usr/bin/env python3
import os
import copy

# Global variables for current files
CURRENT_INVENTORY_FILENAME = "inventory.ini"
CURRENT_TRUENAS_FILENAME = "truenas-servers.yml"

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

def section_servers():
    servers_info = []
    while True:
        hostname = input("Enter a truenas server hostname (or press Enter to finish): ")
        if not hostname:
            break
        token = input(f"Enter token for {hostname}: ")

        # Get input for validate_certs
        while True:
            validate_certs_input = input("Do you want to validate certs for this server? (yes/no): ").strip().lower()
            if validate_certs_input in ['yes', 'no']:
                validate_certs = validate_certs_input == 'yes'
                break
            print("Invalid input. Please enter 'yes' or 'no'.")

        servers_info.append({
            "hostname": hostname, 
            "token": token,
            "validate_certs": validate_certs
        })
    return servers_info

def create_ansible_content():
    sections = {}
    sections["all:vars"] = {"ansible_become_password": input("Enter ansible_become_password: ")}
    sections["ubuntu_nodes"] = section_ubuntu_nodes()

    if sections["ubuntu_nodes"]:
        sections["ubuntu_nodes:vars"] = {"ansible_user": input("Enter common ansible_user for all ubuntu nodes: ")}

    pihole_nodes_list = section_pihole_nodes()
    sections["pihole_nodes"] = [f"{node[0]} ansible_user={node[1]}" for node in pihole_nodes_list]

    return sections

def create_truenas_content():
    return {"servers": section_servers()}

def preview_and_edit(section_fetcher, content_renderer):
    original_sections = section_fetcher()
    sections = copy.deepcopy(original_sections)  # Start with a fresh copy of the original content
    
    while True:
        content = content_renderer(sections)
        print("\n----------------------------------------")
        print(content)
        print("----------------------------------------")
        
        # Display section numbers after the preview
        section_names = list(sections.keys())
        for idx, name in enumerate(section_names, 1):
            print(f"{idx}. {name}")

        # Edit
        section_to_edit = input("\nEnter the section number you'd like to edit (or 'done' to finish): ").strip()
        if section_to_edit.lower() == 'done':
            break

        section_to_edit = int(section_to_edit) - 1
        section_name = section_names[section_to_edit]

        if "vars" in section_name:
            print(f"\nEditing {section_name}...")
            for key, value in sections[section_name].items():
                new_val = input(f"{key} (currently {value}): ").strip()
                if new_val:
                    sections[section_name][key] = new_val

        elif section_name == "servers":
            print(f"\nEditing {section_name}...")
            servers = sections[section_name]
            new_servers = []
            for idx, server in enumerate(servers):
                print(f"\nEditing server {idx+1} details:")
                new_hostname = input(f"hostname (currently {server['hostname']}): ").strip() or server['hostname']
                new_token = input(f"token (currently {server['token']}): ").strip() or server['token']
                new_validate_certs = input(f"validate_certs (currently {server['validate_certs']}): ").strip()
                new_validate_certs = server['validate_certs'] if not new_validate_certs else (True if new_validate_certs.lower() == 'true' else False)

                new_servers.append({
                    'hostname': new_hostname,
                    'token': new_token,
                    'validate_certs': new_validate_certs
                })
            sections[section_name] = new_servers

        else:
            items = sections[section_name]
            print(f"\nEditing {section_name}...")
            new_items = []
            for i, item in enumerate(items, 1):
                new_item = input(f"Item {i} (currently {item}): ").strip()
                new_items.append(new_item if new_item else item)
            sections[section_name] = new_items

    # Ask user whether to save or discard changes
    save_changes = input("Do you want to save the changes? (yes/no): ").strip().lower()
    if save_changes == "yes":
        return True, content  # Return True indicating the changes should be saved
    else:
        print("Discarding changes...")
        return False, content_renderer(original_sections)  # Return False indicating the changes were discarded

def edit_existing(file_type):
    filename = CURRENT_INVENTORY_FILENAME if file_type == 'inventory' else CURRENT_TRUENAS_FILENAME
    if not os.path.exists(filename):
        print(f"\n{filename} doesn't exist yet. Generate it first.\n")
        return

    with open(filename, 'r') as file:
        content = file.read()
    
    if filename == "inventory.ini":
        sections = parse_inventory_ini(content)
        save_status, updated_content = preview_and_edit(lambda: sections, render_ansible_content)
    elif filename == "truenas-servers.yml":
        sections = parse_truenas_servers_yml(content)
        save_status, updated_content = preview_and_edit(lambda: sections, render_truenas_content)
    else:
        print("Unknown file format!")
        return

    if save_status:
        with open(filename, 'w') as file:
            file.write(updated_content)

def parse_inventory_ini(content):
    sections = {}
    current_section = None
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            if "vars" in current_section:  # For sections like all:vars or ubuntu_nodes:vars
                sections[current_section] = {}
            else:
                sections[current_section] = []
        else:
            if "vars" in current_section:
                key, value = line.split("=")
                sections[current_section][key] = value
            else:
                sections[current_section].append(line)

    return sections

def parse_truenas_servers_yml(content):
    lines = content.split("\n")
    servers_section = []
    current_server = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if line == "servers:":
            continue
        
        if line.startswith("- hostname:"):
            if current_server:
                servers_section.append(current_server)
                current_server = {}
            current_server['hostname'] = line.split(":")[1].strip()
        elif line.startswith("token:"):
            current_server['token'] = line.split(":")[1].strip()
        elif line.startswith("validate_certs:"):
            current_server['validate_certs'] = line.split(":")[1].strip() == "true"

    if current_server:
        servers_section.append(current_server)
    
    return {'servers': servers_section}

def render_ansible_content(sections):
    content = []
    for section, items in sections.items():
        if "vars" in section:
            content.append(f"[{section}]")
            for key, value in items.items():
                content.append(f"{key}={value}")
        else:
            content.append(f"[{section}]")
            content.extend(items)
        content.append("")  # Add an empty line after each section for clarity
    return "\n".join(content).rstrip("\n")

def render_truenas_content(sections):
    servers = sections.get('servers', [])
    rendered_servers = []

    for server in servers:
        rendered_servers.append("- hostname: " + server['hostname'])
        rendered_servers.append("  token: " + server['token'])
        rendered_servers.append("  validate_certs: " + str(server['validate_certs']).lower())

    return "\n".join(["servers:"] + rendered_servers)


def interactive_prompt():
    while True:
        print("\nWorking with:")
        print(f"Inventory: {CURRENT_INVENTORY_FILENAME}")
        print(f"TrueNAS Servers: {CURRENT_TRUENAS_FILENAME}")
        print("\nAvailable options:")
        print("1) Generate new inventory.ini")
        print("2) Generate new truenas-servers.yml")
        print("3) Print out existing inventory.ini")
        print("4) Print out existing truenas-servers.yml")
        print("5) Edit existing inventory.ini")
        print("6) Edit existing truenas-servers.yml")
        print("7) Set inventory filename")
        print("8) Set truenas servers filename")
        print("9) Run ansible playbooks")
        print("0) Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            generate_new('inventory')
        elif choice == "2":
            generate_new('truenas')
        elif choice == "3":
            print_existing("inventory")
        elif choice == "4":
            print_existing("truenas")
        elif choice == "5":
            edit_existing("inventory")
        elif choice == "6":
            edit_existing("truenas")
        elif choice == '7':
            set_filename('inventory')
        elif choice == '8':
            set_filename('truenas')
        elif choice == "9":
            run_ansible_playbook()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please select a valid option.")

def print_existing(file_type):
    filename = CURRENT_INVENTORY_FILENAME if file_type == 'inventory' else CURRENT_TRUENAS_FILENAME
    try:
        with open(filename, 'r') as f:
            print(f"\nContent of {filename}:\n")
            print(f.read())
    except FileNotFoundError:
        print(f"\n{filename} does not exist. Please generate the file first.")


def set_filename(file_type):
    """Set the working filename for the current session."""
    global CURRENT_INVENTORY_FILENAME, CURRENT_TRUENAS_FILENAME
    print(f"Current {file_type} filename: {CURRENT_INVENTORY_FILENAME if file_type == 'inventory' else CURRENT_TRUENAS_FILENAME}")
    new_filename = input(f"Enter new {file_type} filename or press Enter to keep the current: ").strip()
    if new_filename:
        if file_type == 'inventory':
            CURRENT_INVENTORY_FILENAME = new_filename
        else:
            CURRENT_TRUENAS_FILENAME = new_filename

def save_to_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)
    print(f"\nSaved to {filename}.")


def run_ansible_playbook():
    print("\nAvailable playbooks:")
    print("1) update-all.sh")
    print("2) update-packages.sh")
    print("3) update-pihole.sh")
    print("4) update-truenas.sh")
    print("0) Go back")

    choice = input("\nWhich playbook do you want to run?: ").strip()
    
    playbooks = {
        "1": "./update-all.sh",
        "2": "./update-packages.sh",
        "3": "./update-pihole.sh",
        "4": "./update-truenas.sh"
    }

    if choice in playbooks:
        os.system(playbooks[choice])
    elif choice == "0":
        return
    else:
        print("Invalid choice. Please select a valid playbook.")

def generate_new(file_type):
    content = None
    if file_type == 'inventory':
        content = main_generate_ansible_inventory()  # Adjusted to use the returned content
    else:
        content = main_generate_truenas()  # Adjusted to use the returned content

    print("\nGenerated content:\n")
    print(content)
    
    save_option = input(f"\nDo you want to save as '{CURRENT_INVENTORY_FILENAME if file_type == 'inventory' else CURRENT_TRUENAS_FILENAME}'? (yes/no/new): ").strip().lower()
    
    if save_option == 'yes':
        save_to_file(content, CURRENT_INVENTORY_FILENAME if file_type == 'inventory' else CURRENT_TRUENAS_FILENAME)
    elif save_option == 'new':
        new_filename = input(f"Enter new {file_type} filename: ").strip()
        save_to_file(content, new_filename)


def main_generate_ansible_inventory():
    _, ansible_content = preview_and_edit(create_ansible_content, render_ansible_content)
    return ansible_content

def main_generate_truenas():
    _, truenas_content = preview_and_edit(create_truenas_content, render_truenas_content)
    return truenas_content

if __name__ == "__main__":
    interactive_prompt()
