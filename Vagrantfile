# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.ssh.username = "root"
  config.ssh.password = "cloudbolt"
  config.vm.define "cloudbolt" do |cb|
    cb.vm.hostname = "vagrant-cloudbolt"
    cb.vm.box = "cloudbolt-8.6"
    cb.vm.box_url = "http://downloads.cloudbolt.io/vagrant/cloudbolt-8.6.box"
    
    if ENV['PUBLIC_NETWORK']
      cb.vm.network("public_network")
    else
      cb.vm.network("private_network", type:"dhcp")
    end
   
    cb.vm.provider "virtualbox" do |vm|
      vm.default_nic_type = "virtio"
      vm.memory = 4096
      vm.cpus = 2
      vm.gui = false
    end

  end

  if ENV['PUBLIC_NETWORK'] then
    config.vm.provision "shell", run: "always", path: "routing.sh"
    config.vm.provision "shell", path: "dev_env.sh"
  end

  config.trigger.after [:up, :resume, :reload] do |trigger|
    trigger.run_remote = {inline: "echo Cloudbolt available at $(ifconfig eth1| egrep -o 'inet addr[^ ]+');"}
  end

end
