VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "ubuntu/trusty64"

  config.vm.provider :virtualbox do |vb|
    vb.name = "realms-wiki"
    vb.memory = 2048
    vb.cpus = 2
  end

  config.vm.synced_folder "srv/", "/srv/"
  config.vm.synced_folder ".", "/home/deploy/realms"
  config.vm.provision :salt do |salt|
  	salt.minion_config = "srv/minion"
	salt.run_highstate = true
  end
end

Vagrant::Config.run do |config|
  config.vm.forward_port 80, 8080
  config.vm.forward_port 4567, 4567
end
