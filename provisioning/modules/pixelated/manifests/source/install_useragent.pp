# install useragent in a virtualenv, deploy helper script
# and make sure venv is activated on login
class pixelated::source::install_useragent {

  $virtualenv_path = '/home/vagrant/user-agent-venv'

  exec { 'install-pixelated':
    # use of "user" parameter doesn't set env variables right,
    # see https://projects.puppetlabs.com/issues/23053
    # therefore we need to explicitily set them here
    environment => [ 'USERNAME=vagrant', 'HOME=/home/vagrant' ],
    command     => "/vagrant/install-pixelated.sh -v \"${virtualenv_path}\" -n /home/vagrant/boxed_node_modules",
    cwd         => '/vagrant',
    user        => 'vagrant',
    # to debug use this
    # logoutput   => true,
    timeout     => 0
  }

  file { '/home/vagrant/activate_custom_node_modules.sh':
    owner  => 'vagrant',
    mode   => '0755',
    source => 'puppet:///modules/pixelated/activate_custom_node_modules.sh',
  }

  exec { 'add_custom_node_modules_to_bashrc':
    command => "/bin/bash -c 'echo \"source /home/vagrant/user-agent-venv/bin/activate\" >> /home/vagrant/.bashrc'",
    unless  => "/bin/grep \"source /home/vagrant/user-agent-venv/bin/activate\" /home/vagrant/.bashrc",
    user    => 'vagrant',
    require => [Exec['install-pixelated'], File['/home/vagrant/activate_custom_node_modules.sh']]
  }
  exec { 'add_custom_node_path_to_bashrc':
    command => "/bin/bash -c 'echo NODE_PATH=/home/vagrant/boxed_node_modules/node_modules/ >> /home/vagrant/.bashrc'",
    unless  => "/bin/grep NODE_PATH /home/vagrant/.bashrc",
    user    => 'vagrant',
  }
}
