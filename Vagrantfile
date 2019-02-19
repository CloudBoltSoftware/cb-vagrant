# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.ssh.username = "root"
  config.ssh.password = "cloudbolt"
  config.vm.define "cloudbolt" do |cb|
    cb.vm.hostname = "vagrant-cloudbolt"
    cb.vm.box = "cloudbolt-8.5"
    cb.vm.box_url = "http://downloads.cloudbolt.io/vagrant/cloudbolt-8.5.box"
    
    # Add a bridged network connection to ensure that this VM can be accessed
    # by the host without port forwarding.
    cb.vm.network "public_network"

    cb.vm.provider "virtualbox" do |vm|
      vm.default_nic_type = "virtio"
      vm.memory = 4096
      vm.cpus = 2
      vm.gui = false
    end

  end

  # Set default router -- we want to route everything through the host system
  # to ensure that applicable packets are routed over the host's VPN.
  # NOTE: this means that a VPN to the CB network is required, even if the local
  # network, e.g. office network, is bridged to the CB network.
  config.vm.provision "shell", 
    run: "always",
    inline: "route add default gw 10.0.2.2"

  # Delete default gw on eth1 which we're assuming is the bridged network.
  config.vm.provision "shell",
    run: "always",
    inline: "eval `route -n | awk '{ if ($8 ==\"eth1\" && $2 != \"0.0.0.0\") print \"route del default gw \" $2; }'`"

  config.trigger.after [:up, :resume, :reload] do |trigger|
    trigger.run_remote = {inline: "echo Cloudbolt available at $(ifconfig eth1| egrep -o 'inet addr[^ ]+');"}
  end

end
