# Base image
FROM ubuntu:20.04

# Set environment variable to prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Ansible installation and basic setup
RUN apt-get update && apt-get install -y software-properties-common && \
    apt-add-repository --yes --update ppa:ansible/ansible && \
    apt-get install -y ansible

# Install required packages and tools
RUN apt-get install -y python3-pip && \
    pip3 install jmespath

# Copy ansible code from the current directory
COPY ./ /ansible/

# Set the working directory to /ansible
WORKDIR /ansible

# Set the environment variable for Ansible to use the private key
ENV ANSIBLE_PRIVATE_KEY_FILE=/etc/ssh_keys/id_rsa

# Set for Ansible to not use Strict Host Key checking (avoid hang on prompt)
ENV ANSIBLE_HOST_KEY_CHECKING=False

# Default command for the container
CMD ["ansible-playbook", "-i", "/etc/inventory/inventory.ini", "playbook.yml"]
