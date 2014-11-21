 Setup for developers
=====================
The following instructions describe how to setup a Vagrant box for development. You need to have Vagrant installed on your system.

# Vagrant setup

Create and provision Vagrant box
```sh
$ vagrant up
```

# Running the server
Activate virtualenv and run Pixelated server:
```sh
$ cd /vagrant/service
$ virtualenv ./.virtualenv
$ source .virtualenv/bin/activate
$ pip install -r requirements.txt
$ pixelated-user-agent --host 0.0.0.0
```

After this you will be asked to setup a LEAP provider. Once entering valid LEAP credentials, you should have the server running.

You should now be able to access the web app by typing localhost:3333 on any browser running on your host machine.
