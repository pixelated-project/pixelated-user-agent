Pixelated User Agent
====================

[![Build Status](https://snap-ci.com/pixelated/pixelated-user-agent/branch/master/build_image)](https://snap-ci.com/pixelated/pixelated-user-agent/branch/master) [
![Coverage Status](https://coveralls.io/repos/pixelated/pixelated-user-agent/badge.svg?branch=master)](https://coveralls.io/r/pixelated/pixelated-user-agent?branch=master)

The Pixelated User Agent is the mail client of the Pixelated ecosystem. It is composed of two parts, a web interface written in JavaScript ([FlightJS](https://flightjs.github.io/)) and a Python API that interacts with a LEAP Provider, the e-mail platform that Pixelated is built on.

Here's a [podcast](https://soundcloud.com/thoughtworks/pixelated-why-secure-communication-is-essential) that explains the project.

**Pixelated is still in early development state!**

![High level architecture User Agent](https://raw.githubusercontent.com/pixelated/website/master/assets/images/pixelated-user-agent.png)

## Try it!

If you are curious,  have a look at the pixelated web client, it as simple as clicking *[here!](https://try.pixelated-project.org:8080/)*

## Getting started

You are most welcome to contribute to the pixelated user agent code base. Please have a look at the [contributions how to](https://github.com/pixelated/pixelated-user-agent/blob/master/CONTRIBUTING.md).

## Installing Pixelated

You like the idea and you want to run it locally, then before you have to install the following packages:

* [Vagrant](https://www.vagrantup.com/downloads.html), Vagrant is a tool that automates the setup of a virtual machine with the development environment
* A vagrant [compatible provider](https://www.vagrantup.com/docs/providers/), e.g. [Virtual   Box](https://www.virtualbox.org/wiki/Downloads).

### Option 1: Pixelated User Agent without LEAP provider

1) Clone the repo and start the virtual machine (downloads 600MB, you may want get a coffee or tea in the meantime):

```
$ git clone https://github.com/pixelated/pixelated-user-agent.git
$ cd pixelated-user-agent
$ vagrant up
```

2) Log into the VM:

```
$ vagrant ssh
```

3) Register with a LEAP provider. You can create a developer account at our [Dev Provider](https://dev.pixelated-project.org/). Please contact us at team@pixelated-project.org for an invite code.

4) Run the user agent:

Please note: If you don't have an account on any provider, go directly to step 5b).

```
$ pixelated-user-agent --host 0.0.0.0

Which provider do you want to connect to:
dev.pixelated-project.org

What’s your username registered on the provider:
username (the one you created in previous step)

Type your password:
******** (the one you created in previous step)
```

5a) Connect to the provider using your credentials, as shown in step 4 above. If the user agent starts up successfully, you will not see any other output.

**Note**: For more convenience during development, you can also create a config file with your credentials (see **Further Notes**).

5b) If you don't have a `dev.pixelated-project.org` account or just want to connect to our `try.pixelated-project.org` environment, we have some sample configurations for you.

Please navigate to the project root in your vagrant box with: `$ cd /vagrant`

Then you can connect to `try.pixelated-project.org` ...

* as Alice via: `$ pixelated-user-agent --host 0.0.0.0 -c try.alice.ini`
* as Bob via: `$ pixelated-user-agent --host 0.0.0.0 -c try.bob.ini`

6) Go to [localhost:3333](http://localhost:3333/). You should see a loading screen for a few seconds, then your inbox. If it sticks on the loading screen, check your terminal for errors, then [get help](https://pixelated-project.org/faq/#contact-the-project).

7) If you like console output, you can also run the tests to see if everything went according to plan.

```bash
(user-agent-venv)vagrant@jessie:~$ cd /vagrant
```

To run the backend tests:

```bash
 (user-agent-venv)vagrant@jessie:/vagrant$ cd service
 (user-agent-venv)vagrant@jessie:/vagrant/service$ ./go test
 (user-agent-venv)vagrant@jessie:/vagrant/service$ cd ..
```

To run the frontend tests:

```bash
 (user-agent-venv)vagrant@jessie:/vagrant$ cd web-ui
 (user-agent-venv)vagrant@jessie:/vagrant/web-ui$ ./go test
 (user-agent-venv)vagrant@jessie:/vagrant/web-ui$ cd ..
```

To run the functional tests:

```bash
 (user-agent-venv)vagrant@jessie:/vagrant$ cd service
 (user-agent-venv)vagrant@jessie:/vagrant/service$ ./go functional
 (user-agent-venv)vagrant@jessie:/vagrant/service$ cd ..
```

7) You're all set! We've prepared [a couple of issues labeled "Volunteer Task"](https://github.com/pixelated/pixelated-user-agent/labels/Volunteer%20task) that are a good place to dive into the project. Happy Hacking!

## Option 2: Pixelated User Agent + Leap Platform

You can install the Pixelated User Agent and the Leap Platform at once, just by running the following command on your console (this may take a while, please be patient):

```bash
 curl https://raw.githubusercontent.com/pixelated/puppet-pixelated/master/vagrant_platform.sh | sh
```

 Once installed, you can create accounts by visiting the LEAP Webapp at [localhost:4443/signup](https://localhost:4443/signup) and see Pixelated in action at [localhost:8080](https://localhost:8080/).

 NOTE: Be aware that you will not be able to send mails outside, but you can test sending mails internally from one user to another.

## Running tests inside your local IDE

If you want to run the tests in your IDE on your host machine outside of vagrant, set up your python virtualenv

```
$ pip install virtualenv setuptools
$ cd ~
$ virtualenv pixelated
$ virtualenv -p [PATH/TO/YOUR/PYTHON/EXECUTABLE] pixelated
$ source ~/.virtualenv/pixelated/bin/activate
```

If you want to run the tests in your IDE on your host machine outside of vagrant, there's a bug in a LEAP library that can't handle symlinks to your local GPG installation.
To fix it, add the path to your GPG binary to your $PATH so that it is found before the symlink in `/usr/local/bin` (or similar).
See also, installations on native OS [below](#developer-setup-on-native-os).


## How do I see the result of my changes?

For all **Python changes**, you will need to kill (Ctrl-C) the server and run `$ pixelated-user-agent --host 0.0.0.0` again.

For most **JavaScript** or **HTML changes**, you will just need to reload the browser.

For most **CSS or Handlebars templates changes**, you will also need to run: `$ cd /vagrant/web-ui && ./go build`

## I think I might be able to hack together a quick-and-dirty lo-fi solution for the issue I’m working with… what do I do?

Do it the easy way first, and submit a pull request as a “work in progress” as soon as you have a quick-and-dirty solution (or even an unfinished solution) — that means you can get feedback from the other developers about whether you’re heading in the right direction sooner rather than later. Include “WIP” (work in progress) in the description of your pull request and ask for review, or feedback on anything specific.

# Further Notes

## Multi User Mode

To run the pixelated user agent multi user mode, please run the following:
```bash
 (user-agent-venv)vagrant@jessie:/vagrant$ pixelated-user-agent --host 0.0.0.0 --multi-user --provider=dev.pixelated-project.org
```

You will need to change `dev.pixelated-project.org` to the hostname of the leap provider that you will be using.
Once that is done, you can use by browsing to [http://localhost:3333](http://localhost:3333), where you will be prompted for your email username and password.

## Config file with credentials

The config file has to be in `ini` format, see for example
`try.alice.ini` or `try.bob.ini` in the root directory, or this one:

*credentials.ini*
```
[pixelated]
leap_server_name=dev.pixelated-project.org
leap_username=<your_username>
leap_password=<your_password>
```
To use it start the user agent like this:
`$ pixelated-user-agent --host 0.0.0.0 --config credentials.ini`

You can also include the host in the config file, as shown in the example files given above.

## Self-signed provider certs

You might also need to add your LEAP provider ssl certificate to pixelated manually for now, with the following steps:

The easiest way to get this is downloading if from https://your.provider.org/ca.crt.
Rename the certificate based on your provider domain name like this `your.leapprovider.org.crt` and put it into `services/pixelated/certificates/`.


## Continuous Integration
All commits to the pixelated user agent code trigger all tests to be run in [snap-ci](https://snap-ci.com/pixelated/pixelated-user-agent/branch/master).

## Misc
* You can access the guest OS shell via the command `vagrant ssh` run within the `pixelated-user-agent/` folder in the host OS.
* `/vagrant/` in the guest OS is mapped to the `pixelated-user-agent/` folder in the host OS. File changes on either side will reflect in the other.
* First time email sync could be slow, please be patient. This could be the case if you have a lot of emails already and it is the first time you setup the user agent on your machine.
* CTRL + \ will stop the server.
* For all backend changes, you will need to stop and restart the server again (Step 5 above).
* For most frontend changes, you will just need to reload the browser. Some changes (in particular, those involving css or handlebars) you will need to run:
```bash
 (user-agent-venv)vagrant@jessie:/vagrant$ cd web-ui
 (user-agent-venv)vagrant@jessie:/vagrant/web-ui$ ./go build
```

## Developer Setup On Native OS

Please ensure that you have an email user from your preferred leap provider ([How to](#registering-with-a-leap-provider)).
Details for developer installations [on OSX](#on-osx) and [Debian distributions](#on-debian-distributions) are explained below.
In case of any issues, please ping us on IRC ([#pixelated on irc.freenode.net](irc://irc.freenode.net/pixelated)), we will be available to help you from there.

### On OSX

First, you will need to install the [GPG tools](https://gpgtools.org/) for Mac.
Then, run the following sequence of commands:
```bash
$ curl https://raw.githubusercontent.com/pixelated/pixelated-user-agent/master/osx_setup.sh | sh
$ cd pixelated-user-agent && source ~/.virtualenv/user-agent-venv/bin/activate
```

Please note that you will have to activate the virtualenv anytime you work on a different terminal. This is done by simply running `$ source ~/.virtualenv/user-agent-venv/bin/activate` first.

Running the user agent and the various tests are the same as in the vagrant setup in step 5) and 8) above.

### On Debian distributions

This is the setup for developers. Please run the following commands:

```bash
$ curl https://raw.githubusercontent.com/pixelated/pixelated-user-agent/master/debian_setup.sh | bash
$ cd pixelated-user-agent && source ~/.virtualenv/user-agent-venv/bin/activate
```

Please note that you will have to activate the virtualenv anytime you work on a different terminal. This is done by simply running `$ source ~/.virtualenv/user-agent-venv/bin/activate` first.

Running the user agent and the various tests are the same as in the vagrant setup in step 5) and 8) above.

## Debian package

For people that just want to try the user agent, we have debian packages available in our [repository](http://packages.pixelated-project.org/debian/). To use it, you have to add it to your sources list:

```shell

echo "deb [arch=amd64] http://packages.pixelated-project.org/debian jessie-snapshots main" > /etc/apt/sources.list.d/pixelated.list

apt-key adv --keyserver pool.sks-keyservers.net --recv-key 287A1542472DC0E3

apt-get update

apt-get install pixelated-user-agent
```

for multi-user mode, change the last line above to
```shell
apt-get install pixelated-server
```

## Docker

For people who want to run the user agent on docker container can use the Dockerfile.

## How to translate the user interface

See: [Contributor's Guide](https://github.com/pixelated/pixelated-user-agent/blob/master/CONTRIBUTING.md#translating-ui)
