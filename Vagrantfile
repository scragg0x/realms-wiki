Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.provider :virtualbox do |vb|
    vb.name = "realms-wiki"
    vb.memory = 512
    vb.cpus = 2
  end

  config.vm.provision "shell", path: "provision.sh", privileged: false
  config.vm.network "forwarded_port", guest: 5000, host: 5000
end
