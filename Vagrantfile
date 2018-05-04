# -*- mode: ruby -*-
# vi: set ft=ruby :

# PYWA Vagrantfile

VAGRANTFILE_API_VERSION = "2"

# Ansible install script for Ubuntu
$ansible_install_script = <<SCRIPT
export DEBIAN_FRONTEND=noninteractive
echo check if Ansible exists...
if ! which ansible >/dev/null; then
  echo update package index files...
  apt-get update -qq
  echo install Ansible...
  apt-get install -qq ansible
fi
SCRIPT

$ansible_local_provisioning_script = <<SCRIPT
export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1
echo provisioning with Ansible...
ansible-playbook -u vagrant /vagrant/provisioning/playbook.yml -i /vagrant/provisioning/ansible_hosts -c local
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "bento/ubuntu-18.04"
  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end
  # sync current dir (wasn't happening automatically on Windows)
  config.vm.synced_folder ".", "/vagrant"
  # forward ports
  config.vm.network :forwarded_port, host: 3000, guest: 3000
  config.vm.network :forwarded_port, host: 3001, guest: 3001
  # turn off warning message `stdin: is not a tty error`
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
  # be sure that there  is Ansible for local provisioning
  config.vm.provision "shell", inline: $ansible_install_script
  # do the final Ansible local provisioning
  config.vm.provision "shell", inline: $ansible_local_provisioning_script
end
