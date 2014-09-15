VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provider :virtualbox do |vb|
    vb.name = "realms-wiki"
    vb.memory = 2048
    vb.cpus = 2
  end

  config.vm.provision "shell", path: "install.sh"
end

Vagrant::Config.run do |config|
  config.vm.forward_port 5000, 5000
end
