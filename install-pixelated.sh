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
pip install --upgrade setuptools
./go setup --always-unzip
pip uninstall -y enum34 && pip install enum34
pip uninstall -y pysqlcipher && pip install pysqlcipher # this is needed so pysqlcipher gets recompiled with the right version of glibc

# print usage
cat <<EOF

###############

## You will need an account in a LEAP provider with mail support. You may find some at http://bitmask.net/

## You might also need to add your LEAP provider ssl certificate to pixelated manually for now, with the following steps:
## The easiest way to find this is accessing https://your.provider.org/ca.crt
## Rename the certificate based on your provider domain name like this 'your.leapprovider.org.crt'
## Put it in services/pixelated/certificates/

## Once you are done, activate your virtual environment by running:
## source $VIRTUALENV_PATH/bin/activate

## The User agent will be available on localhost:3333 after running
## pixelated-user-agent

EOF
