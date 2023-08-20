# Use the latest Ubuntu LTS as a base image
FROM ubuntu:20.04

# Set environment variable to prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Key will be mounted by Kubernetes Volume
ENV ANSIBLE_PRIVATE_KEY_FILE=/etc/ssh_keys/id_rsa

# Update and install required software packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-add-repository --yes --update ppa:ansible/ansible && \
    apt-get install -y ansible python3-pip && \
    apt-get clean

# Install 'jmespath' using pip
RUN pip3 install jmespath

# Copy the Ansible code from the local directory into the container
COPY . /ansible-code/

# Set the working directory
WORKDIR /ansible-code

# By default, run the playbook when the container starts, replace "your_playbook.yml" with the name of your playbook
CMD ["ansible-playbook", "your_playbook.yml"]
