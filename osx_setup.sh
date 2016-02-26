#!/bin/bash

function install_compass {
    rbenv install -s 2.2.3
    eval "$(rbenv init -)"
    rbenv shell 2.2.3
    rbenv local 2.2.3
    gem install compass
    export PATH=$PATH:~/.rbenv/versions/2.2.3/bin
    echo "export PATH=$PATH:~/.rbenv/versions/2.2.3/bin" | tee ~/.zshrc ~/.bash_profile > /dev/null
    echo 'eval "$(rbenv init -)"' >> ~/.bash_profile
}

function install_rbenv {
    hash rbenv 2>/dev/null || brew install rbenv ruby-build
}

function install_npm {
    hash node 2>/dev/null || brew install npm
}

function clone_repo {
    if [ -d ./pixelated-user-agent ]
    then
      cd pixelated-user-agent
      /usr/bin/git pull --rebase
      rm -rf web-ui/node_modules
    else
      /usr/bin/git clone https://github.com/pixelated/pixelated-user-agent.git
      cd pixelated-user-agent
    fi
}
#setup frontend
install_rbenv
install_compass
install_npm

#setup backend
brew install python # force brew install even if python is already installed
export  LDFLAGS=-L/usr/local/opt/openssl/lib
export  LDFLAGS=-L/usr/local/opt/openssl/lib
pip install virtualenv

# install
clone_repo
./install-pixelated.sh -v ~/.virtualenv/user-agent-venv
