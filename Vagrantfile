VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise64"
  config.vm.synced_folder "srv/", "/srv/"
  config.vm.synced_folder ".", "/home/deploy/realms"
  config.vm.provision :salt do |salt|
  	salt.minion_config = "srv/minion"
	salt.run_highstate = true
  end
end

Vagrant::Config.run do |config|
  config.vm.forward_port 80, 8000
  config.vm.forward_port 5432, 5432
  config.vm.forward_port 10000, 10000
end
