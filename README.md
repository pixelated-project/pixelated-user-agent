Pixelated User Agent
====================
[![Build Status](https://snap-ci.com/pixelated-project/pixelated-user-agent/branch/master/build_image)](https://snap-ci.com/pixelated-project/pixelated-user-agent/branch/master)

The Pixelated User Agent is the mail client of the Pixelated ecosystem, it is composed of two parts, a web interface written in javascript and an API written in python that glues that interface with the Pixelated or LEAP Provider.

**Pixelated is still in early development state!**

![High level architecture User Agent](https://pixelated-project.org/assets/images/pixelated-user-agent.png)

## Getting started

### Registering with a provider

  * You can create a developer account at our [Dev Provider](https://dev.pixelated-project.org/).
  * There are some other LEAP providers on the [Bitmask page](https://bitmask.net), but they don't support email currently.
  * If you want to run your own provider, see [pixelated-platform](https://github.com/pixelated-project/pixelated-platform).

### Requirements
  * vagrant
  * virtualbox

Clone the repository:

    git clone https://github.com/pixelated-project/pixelated-user-agent.git
    cd pixelated-user-agent

From the project root folder, set up the vagrant machine:

    vagrant up source

You can log into the machine and view project root folder with:

    vagrant ssh
    
 Then you need to run the setup:
 
    cd service
    ./go setup
    
From here on you can run the tests for the UI by going to the **web-ui** folder or for the API by going to the **service** folder:

    cd /vagrant/web-ui
    ./go test
    
    cd /vagrant/service
    ./go test
Running the user agent:

```
$ pixelated-user-agent --host 0.0.0.0 -lc /vagrant/service/pixelated/certificates/dev.pixelated-project.org.ca.crt
> 2015-01-23 11:18:07+0100 [-] Log opened.
> 2015-01-23 11:18:07+0100 [-] Which provider do you want to connect to:
dev.pixelated-project.org
> 2015-01-23 11:18:52+0100 [-] What's your username registered on the provider:
username
> Type your password:
*******************
```

As soon as the agent starts you will be asked for username, password and the [provider you registered with](https://github.com/pixelated-project/pixelated-user-agent/blob/master/README.md#registering-with-a-provider). 

Now you can see it running on [http://localhost:3333](http://localhost:3333)

##Debian package

For people that just want to try the user agent, we have debian packages available in our [repository](http://packages.pixelated-project.org/debian/). To use it you have to add it to your sources list:

```shell

echo "deb http://packages.pixelated-project.org/debian wheezy-snapshots main" > /etc/apt/sources.list.d/pixelated.list
echo "deb http://packages.pixelated-project.org/debian wheezy-backports main" >> /etc/apt/sources.list.d/pixelated.list
echo "deb http://packages.pixelated-project.org/debian wheezy main" >> /etc/apt/sources.list.d/pixelated.list

apt-key adv --keyserver pool.sks-keyservers.net --recv-key 287A1542472DC0E3

apt-get update

apt-get install pixelated-user-agent
```
