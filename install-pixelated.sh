#!/bin/bash
#
# Copyright (c) 2014 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.

# test dependencies

set -e
export NODE_PATH='/home/vagrant/boxed_node_modules/node_modules/'

if [ ! $USERNAME ]
then
  export USERNAME=`whoami`
fi

usage() { echo "Usage: $0 [-v <virtualenv path>] [-n <custom node modules directory>]" 1>&2; exit 1; }

VIRTUALENV_PATH=".virtualenv"
CUSTOM_NODE_MODULES_LOCATION=""
while getopts "n:v:" OPT; do
    case "${OPT}" in
        v)
            VIRTUALENV_PATH=${OPTARG}
            ;;
        n) # custom node_modules installation
            CUSTOM_NODE_MODULES_LOCATION=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

function check_installed() {
        set +e
        which $1
        if [ $? -ne 0 ]; then
                echo "## You must have ${1} installed and in the PATH to run Pixelated-User-Agent"
                echo "## Check our wiki for more information on dependencies:"
                echo "## https://github.com/pixelated-project/pixelated-user-agent/wiki/Installing-dependencies"
                echo "## exiting..."
                exit 1
        fi
        set -e
}


# The below is necessary to allow node to use enough memory
# so that installing phantomjs won't fail
mkdir -p /home/vagrant/bin
cat > /home/vagrant/bin/node <<EOF
#!/usr/bin/env bash

/usr/bin/node --max_old_space_size=2000 "\$@"
EOF
chmod +x /home/vagrant/bin/node
export PATH=/home/vagrant/bin:$PATH


function install_node_modules_at_custom_location() {
  local LOCATION="$1"
  local WEBUI_DIR=$(pwd)

  if [ -e "$WEBUI_DIR/node_modules" ] ; then
    echo "It seems there is already a node_modules folder" 1>&2
    return
  fi

  if [ ! -e "$LOCATION" ] ; then
    mkdir "$LOCATION"
    pushd "$LOCATION"

    ln -s "$WEBUI_DIR/package.json" package.json
    npm install

    popd
  fi

  if [ ! -h "node_modules" ] ; then
    rm -Rf "node_modules"
    ln -s "$LOCATION/node_modules" node_modules
  fi
}

for dependency in node npm ruby virtualenv git gpg compass; do
        check_installed $dependency
done

# install web-ui dependencies
cd web-ui
UIPATH=`pwd`

if [ -z "$CUSTOM_NODE_MODULES_LOCATION" ] ; then
  npm install
else
  install_node_modules_at_custom_location "$CUSTOM_NODE_MODULES_LOCATION"
fi

node_modules/bower/bin/bower -V install --config.interactive=false --allow-root
LC_ALL=en_US.UTF-8 ./go build

# install service dependencies
cd ../service
rm -rf "$VIRTUALENV_PATH"
virtualenv "$VIRTUALENV_PATH"
source "$VIRTUALENV_PATH/bin/activate"
# they can't be on the same command because it breaks pip upgrade
pip install --upgrade pip
pip install --upgrade setuptools
./go setup --always-unzip
pip uninstall -y enum34 && pip install enum34
pip uninstall -y pysqlcipher && pip install pysqlcipher # this is needed so pysqlcipher gets recompiled with the right version of glibc

# print usage
cat <<EOF

###############

## You will need an account in a LEAP provider with mail support. You can request an invite code for
## https://dev.pixelated-project.org, please refer to point 4) in the [Getting started guide](https://github.com/pixelated/pixelated-user-agent#getting-started).

## Once you are done, activate your virtual environment by running:
## source $VIRTUALENV_PATH/bin/activate

## The User agent will be available on http://localhost:3333 after running:
##     pixelated-user-agent

EOF
