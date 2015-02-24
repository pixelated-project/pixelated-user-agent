# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

new_plugin_installed = false
unless Vagrant.has_plugin?('vagrant-vbguest')
  plugin = 'vagrant-vbguest'
  puts "Missing plugin #{plugin}, installing..."

  `vagrant plugin install #{plugin}`

  new_plugin_installed = true
end
exec "vagrant #{ARGV.join' '}" if new_plugin_installed

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # we need a debian testing vagrantbox because
  # - currently the useragent debian packages depend on python-cryptography which is only
  #   available in debian jessie (for the fernet module to create keys)
  # - the source installation needs npm, which is also only available in debian jessie

  # Please verify the sha512 sum of the downloaded box before importing it into vagrant !
  # see https://leap.se/en/docs/platform/details/development#Verify.vagrantbox.download
  # for details

  config.vm.box = "leap-jessie-amd64"

  config.vbguest.auto_update = false

  config.vm.define "source", primary: true do |source|
    source.vm.provider :virtualbox do |v, override|
      override.vm.box_url = "https://downloads.leap.se/platform/vagrant/virtualbox/leap-debian-jessie-amd64-virtualbox.box"
    end
    source.vm.provider "libvirt" do |v, override|
      override.vm.box_url = "https://downloads.leap.se/platform/vagrant/libvirt/Debian-jessie.beta1-amd64-netboot.box"
    end
    source.vm.provision "puppet" do |puppet|
      puppet.manifests_path = "provisioning/manifests"
      puppet.module_path    = "provisioning/modules"
      puppet.manifest_file  = "source.pp"
    end
  end

  config.vm.define "deb", autostart: false do |deb|
    # until https://github.com/pixelated-project/pixelated-user-agent/issues/226 is not fixed,
    # we depend on a debian testing box

    config.vm.box = "leap-wheezy"
    deb.vm.provider "virtualbox" do |v, override|
      override.vm.box_url = "https://downloads.leap.se/platform/vagrant/virtualbox/leap-wheezy.box"
    end
    deb.vm.provider "libvirt" do |v, override|
      override.vm.box_url = "https://downloads.leap.se/platform/vagrant/libvirt/leap-wheezy.box"
    end
    deb.vm.provision "puppet" do |puppet|
      puppet.manifests_path = "provisioning/manifests"
      puppet.module_path    = "provisioning/modules"
      puppet.manifest_file  = "deb.pp"
    end
  end

  config.vm.define "hackday", autostart: false do |hackday|
    config.vm.box = "hackday-pixelated-user-agent"
  end

  config.vm.network :forwarded_port, guest: 3333, host: 3333 # do NOT add host_ip in this line. It is not necessary

  if /mswin|mingw/ =~ RUBY_PLATFORM
    config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".git/"
  end

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end
end
