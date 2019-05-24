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
      vm.memory = 4096# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.ssh.username = "root"
  config.ssh.password = "cloudbolt"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 4434
  config.vm.define "cloudbolt" do |cb|
    cb.vm.hostname = "vagrant-cloudbolt"
    cb.vm.box = "cloudbolt-8.6"
    cb.vm.box_url = "http://downloads.cloudbolt.io/vagrant/cloudbolt-8.6.box"
    if ENV['PUBLIC_NETWORK']
      cb.vm.network("public_network")
    else
      cb.vm.network("private_network", type:"dhcp")
    end
  config.vm.synced_folder ".", "/vagrant", disabled: false

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

$script = <<-SCRIPT
#!/bin/bash
cp /vagrant/license.bin /var/opt/cloudbolt/license.bin
cp /vagrant/customer_settings.py /var/opt/cloudbolt/proserv/
mkdir -p /var/opt/cloudbolt/proserv/xui
cp -r /vagrant/api_extension /var/opt/cloudbolt/proserv/xui/
service httpd restart
python3 /vagrant/cb_setup.py
SCRIPT

  config.vm.provision :shell do |s|
    s.inline = $script
    s.env= {
      RESOURCEHANDLERNAME:ENV['RESOURCEHANDLERNAME'],
      RESOURCEHANDLERIP:ENV['RESOURCEHANDLERIP'],
      RESOURCEHANDLERDESCRIPTION:ENV['RESOURCEHANDLERDESCRIPTION'],
      RESOURCEHANDLERUSERNAME:ENV['RESOURCEHANDLERUSERNAME'],
      RESOURCEHANDLERPASSWORD:ENV['RESOURCEHANDLERPASSWORD'],
      RESOURCEHANDLERNETWORKNAMES:ENV['RESOURCEHANDLERNETWORKNAMES'],
      RESOURCEHANDLERVIRTUALFOLDERPATH:ENV['RESOURCEHANDLERVIRTUALFOLDERPATH'],
      ENVIRONMENTNAME:ENV['ENVIRONMENTNAME'],
      ENVIRONMENTCLUSTERNAME:ENV['ENVIRONMENTCLUSTERNAME'],
      ENVIRONMENTDATASTORE:ENV['ENVIRONMENTDATASTORE'],
      TEMPLATENAME:ENV['TEMPLATENAME'],
      OSBUILDNAME:ENV['OSBUILDNAME'],
      OSBUILDFAMILY:ENV['OSBUILDFAMILY'],
      OSBUILDENVIRONMENTS:ENV['OSBUILDENVIRONMENTS'],
      TEMPLATEUSERNAME:ENV['TEMPLATEUSERNAME'],
      GITHUBUSERNAME:ENV['GITHUBUSERNAME'],
      GITHUBPASSWORD:ENV['GITHUBPASSWORD'],
      BLUEPRINTFILE:ENV['BLUEPRINTFILE']}
  end
  config.trigger.after [:up, :reload, :resume] do |trigger|
    trigger.run_remote = {inline: "echo Cloudbolt available at $(ifconfig eth1| egrep -o 'inet addr[^ ]+');"}
  end
end

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
