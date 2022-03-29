# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.ssh.username = "root"
  config.ssh.password = "cloudbolt"
  config.vm.define "cloudbolt" do |cb|
    cb.vm.hostname = "vagrant-cloudbolt"
    cb.vm.box = "cloudbolt-9.4.7.1"
    cb.vm.box_url = "https://downloads.cloudbolt.io/vagrant/cloudbolt-9.4.7.1.box"
    
    cb.vm.network("private_network", type:"dhcp")
   
    cb.vm.provider "virtualbox" do |vm|
      vm.default_nic_type = "virtio"
      vm.memory = 4096
      vm.cpus = 2
      vm.gui = false
    end

  end

  config.trigger.after [:up, :resume, :reload] do |trigger|
    trigger.run_remote = {inline: "echo Login to this instance at https://$(hostname -I | cut -d' ' -f2);"}
  end

end
