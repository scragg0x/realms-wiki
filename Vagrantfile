VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise64"
  config.vm.synced_folder "srv/", "/srv/"
  config.vm.provision :salt do |salt|
  	salt.minion_config = "srv/minion"
	salt.run_highstate = true
  end
  config.vm.provider :digital_ocean do |provider, override|
    override.ssh.private_key_path = '~/.ssh/id_dsa'
    override.vm.box = 'digital_ocean'
    override.vm.box_url = "https://github.com/smdahlen/vagrant-digitalocean/raw/master/box/digital_ocean.box"

    provider.client_id = ''
    provider.api_key = ''
  end
end

Vagrant::Config.run do |config|
  config.vm.forward_port 80, 8000
  config.vm.forward_port 10000, 10000
  config.vm.forward_port 20000, 20000
end
