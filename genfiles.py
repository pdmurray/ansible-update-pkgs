#!/usr/bin/env python3
import os
import copy
import yaml

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
            validate_certs_input = input("Enter validate_certs for the server (True/False): ").strip().lower()
            if validate_certs_input in ['true', 'false']:
                validate_certs = validate_certs_input == 'true'
                break
            print("Invalid input. Please enter 'True' or 'False'.")

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

def preview_and_edit(section_fetcher, content_renderer, edit_display_function=None):

    original_sections = section_fetcher()
    sections = copy.deepcopy(original_sections)  # Start with a fresh copy of the original content
    
    while True:
        # Use edit_display_function if provided, otherwise use content_renderer
        display_function = edit_display_function if edit_display_function else content_renderer
        content = display_function(sections)

        print("\n----------------------------------------")
        print(content)
        print("----------------------------------------")
        
        if 'servers' in sections:
            section_names = [server['hostname'] for server in sections['servers']]
        else:
            section_names = list(sections.keys())

        # Special handling if the 'servers' section is empty
        if 'servers' in sections and not sections['servers']:
            print("No servers found.")
            add_new_server = input("Would you like to add a new server? (yes/no): ").strip().lower()
            if add_new_server == 'yes':
                new_server = {}
                
                new_server['hostname'] = input("Enter the hostname for the new server: ").strip()
                if not new_server['hostname']:
                    print("Hostname cannot be empty.")
                    continue  # Go back to the start of the loop
                
                new_server['token'] = input("Enter the token for the new server: ").strip()
                if not new_server['token']:
                    print("Token cannot be empty.")
                    continue  # Go back to the start of the loop

                validate_certs = input("Enter validate_certs for the new server (True/False): ").strip().lower()
                new_server['validate_certs'] = True if validate_certs == 'true' else False
                
                sections['servers'].append(new_server)
                continue  # Go back to the start of the loop to display the updated list


        for idx, name in enumerate(section_names, 1):
            print(f"{idx}. {name}")

        section_to_edit = input("\nEnter the section number you'd like to edit (or 'done' to finish): ").strip()

        # First, handle the 'done' case
        if section_to_edit.lower() == 'done':
            break

        # Now, validate the entered number
        try:
            section_to_edit = int(section_to_edit) - 1
        except ValueError:
            print("Please enter a valid section number or 'done'")
            continue

        # Check if the chosen section number is within range
        if section_to_edit < 0 or section_to_edit >= len(section_names):
            print("Invalid section number. Please choose a valid section or 'done'")
            continue

        section_name = section_names[section_to_edit]

        if "vars" in section_name:
            print(f"\nEditing {section_name}...")
            for key, value in sections[section_name].items():
                new_val = input(f"{key} (currently {value}): ").strip()
                if new_val:
                    sections[section_name][key] = new_val

        elif section_name in [server['hostname'] for server in sections.get('servers', [])]:
            # Find the correct server using the section_name as the hostname
            server_to_edit = next(server for server in sections['servers'] if server['hostname'] == section_name)

            print(f"\nEditing server details for {server_to_edit['hostname']}...")
            
            # Get new hostname with validation
            while True:
                new_hostname = input(f"hostname (currently {server_to_edit['hostname']}): ").strip() or server_to_edit['hostname']
                if new_hostname:
                    break
                print("Hostname cannot be empty.")
            
            # Get new token with validation
            while True:
                new_token = input(f"token (currently {server_to_edit['token']}): ").strip() or server_to_edit['token']
                if new_token:
                    break
                print("Token cannot be empty.")
            
            new_validate_certs = input(f"validate_certs (currently {server_to_edit['validate_certs']}): ").strip()
            new_validate_certs = server_to_edit['validate_certs'] if not new_validate_certs else (True if new_validate_certs.lower() == 'true' else False)
            
            server_to_edit['hostname'] = new_hostname
            server_to_edit['token'] = new_token
            server_to_edit['validate_certs'] = new_validate_certs


        else:
            items = sections[section_name]
            print(f"\nEditing {section_name}...")
            new_items = []
            for i, item in enumerate(items, 1):
                new_item = input(f"Item {i} (currently {item}): ").strip()
                new_items.append(new_item if new_item else item)
            sections[section_name] = new_items

    save_changes = input("Commit these edits? (yes/no): ").strip().lower()
    if save_changes == "yes":
        return True, content_renderer(sections)
    else:
        print("Discarding changes...")
        return False, content_renderer(original_sections)


def edit_existing(file_type):
    filename = CURRENT_INVENTORY_FILENAME if file_type == 'inventory' else CURRENT_TRUENAS_FILENAME
    if not os.path.exists(filename):
        print(f"\n{filename} doesn't exist yet. Generate it first.\n")
        return

    with open(filename, 'r') as file:
        content = file.read()
    
    if file_type == 'inventory':
        sections = parse_inventory_ini(content)
        save_status, updated_content = preview_and_edit(lambda: sections, render_truenas_content)
    elif file_type == 'truenas':
        sections = parse_truenas_servers_yml(content)
        save_status, updated_content = preview_and_edit(lambda: sections, render_truenas_content, display_truenas_for_editing)
    else:
        print("Unknown file format!")
        return

    if save_status:
        with open(filename, 'w') as file:
            file.write(updated_content)
        print("Changes saved successfully!")
    else:
        print("No changes were saved.")



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

def is_valid_truenas_config():
    filename = CURRENT_TRUENAS_FILENAME
    try:
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)

        # Check if it's a dictionary
        if not isinstance(data, dict):
            return False

        # Check for 'servers' key
        if 'servers' not in data:
            return False

        # Validate each server entry
        for server in data['servers']:
            if not all(key in server for key in ['hostname', 'token', 'validate_certs']):
                return False

        return True

    except Exception as e:
        print(f"Error reading file: {e}")
        return False

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

def display_truenas_for_editing(sections):
    content = []
    
    if "servers" in sections:
        servers_content = ["servers:"]
        for idx, server in enumerate(sections["servers"], 1):
            server_repr = f"{idx}. hostname: {server['hostname']}\n   token: {server['token']}\n   validate_certs: {server['validate_certs']}"
            servers_content.append(server_repr)
        content.extend(servers_content)
    return "\n".join(content)


def interactive_prompt():
    while True:
        print("\nWorking with:")
        print(f"Inventory: {CURRENT_INVENTORY_FILENAME}")
        print(f"TrueNAS Servers: {CURRENT_TRUENAS_FILENAME}")
        print("\nAvailable options:")
        print("1) Generate new Inventory")
        print("2) Generate new TrueNAS Config")
        print("3) Print out existing Inventory")
        print("4) Print out existing TrueNAS Config")
        print("5) Edit existing Inventory")
        print("6) Edit existing TrueNAS Config")
        print("7) Set working inventory filename")
        print("8) Set working truenas servers filename")
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
            if not is_valid_truenas_config():
                print(f"{CURRENT_TRUENAS_FILENAME} is not in a valid format. Please fix it before continuing.")
            else:
                print_existing("truenas")
        elif choice == "5":
            edit_existing("inventory")
        elif choice == "6":
            if not is_valid_truenas_config():
                print(f"{CURRENT_TRUENAS_FILENAME} is not in a valid format. Please fix it before continuing.")
            else:
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
        content = main_generate_ansible_inventory()
    else:
        content = main_generate_truenas()
        if content is None:
            return  # Exit the function if there's no valid content

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
    
    truenas_data = yaml.safe_load(truenas_content)
    if not truenas_data.get('servers'):
        print("Error: At least one server must be defined to generate a TrueNAS config.")
        return None

    return truenas_content


if __name__ == "__main__":
    interactive_prompt()
