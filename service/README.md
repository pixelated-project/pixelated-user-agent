ixelated User Agent Service
============================

This is the service for the Pixelated User Agent. The primary purpose of this is to provide an interface for the user agent to communicate with the Pixelated Provider.

The user agent is implemented in Python, for compatibility with the LEAP libraries. Another goal of the User Agent Service will be to run well on all major client platforms. Finally, the main goals are to have strong search, encryption and signing. However, we want to push most of these features back to LEAP so that Bitmask can leverage them as well.


Development environment
---

* Install virtualenv:

```
easy_install virtualenv
```

* Create a virtualenv:

```
virtualenv .virtualenv 
```

* Activate your virtualenv:

```
source .virtualenv/bin/activate
```

* Configure the application

You will need an account in a LEAP provider. Once you have it, modify the service/pixelated.example file and move it to ~/.pixelated

You might need to add your LEAP provider ssl certificate inside the pixelated/certificates named as your provider domain name, for example:

```
your.leapprovider.org.crt
```

* Start the developer mode

```
./go develop --always-unzip
```

* To run tests:

```
./go test
```

* To run app (after starting the developer mode):

```
pixelated-user-agent
```

* For development purposes you can also copy the pixelated.example file and fill in your credentials,
  that way you avoid having to enter your test credentials everytime:
```
pixelated-user-agent --config=<config_file_path>
```

Run a single unit or integration test
```
trial
```
Run a single functional test

```
behave test/functional/features/name_of_feature.feature
```
