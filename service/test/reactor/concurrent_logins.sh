#!/bin/bash
#
# Copyright (c) 2015 ThoughtWorks, Inc.
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


USER_PREFIX="loadtest"
PASSWORD_PREFIX="password_"

PROVIDER="dev.pixelated-project.org"
RUNS=9
USERS=1
SLEEP=1

function show_help {
    echo
    echo "Run several tests against login in the pixelated-user-agent vagrant machine"
    echo
    echo "It saves the logs to service/test/login/metrics"
    echo
    echo " --user|-u - array with amount of tests split by comma"
    echo " --runs|-r - how many times a tests is going to run"
    echo " --provider|-p - set the provider"
    echo " --sleep|-s - time to sleep between requests"
    echo " --help|-h - show help message"
}

function run_on_vagrant {
    vagrant ssh -c "$@" > /dev/null 2>&1
}

function curl_login {
    index=$1
    username=${USER_PREFIX}${index}
    password=${PASSWORD_PREFIX}${index}

    curl -siLD - \
        -w "request time: %{time_total}\n\n\n" \
        -o /dev/null \
        -X POST \
        --data "username=${username}&password=${password}" \
        --cookie 'XSRF-TOKEN: blablabla' \
        --header 'X-Requested-With: XMLHttpRequest' \
        --header 'X-XSRF-TOKEN: blablabla' \
        http://localhost:3333/login |\
    grep '^HTTP\|^request' |\
    tee -a load-test.log |\
    sed 's/\(.*\)/      - \1/'
}

while [[ $# > 0 ]]; do
    case $1 in
        --users|-u)
            USERS=$2
            shift
        ;;
        --runs|-r)
            RUNS=$2
            shift
        ;;
        --provider|-p)
            PROVIDER=$2
            shift
        ;;
        --sleep|-s)
            SLEEP=$2
            shift
        ;;
        --help|-h)
            show_help
            exit 0
        ;;
    esac
    shift
done

run_on_vagrant "pkill pixelated"
run_on_vagrant "rm ~/MetricsTime"
run_on_vagrant "mkdir -p /vagrant/service/test/login/metrics"
run_on_vagrant "sudo ln -s /home/vagrant/user-agent-venv/bin/pixelated-user-agent /usr/local/bin"

for user in $(tr ',' ' ' <<< $USERS); do
    echo "> Run for $user user(s)"

    for run in $(seq $RUNS); do
        echo "  > Running $run of $RUNS runs"
        echo "  > Starting Pixelated UA"

        until curl -s "http://localhost:3333" -o /dev/null 2>&1; do
            run_on_vagrant "nohup pixelated-user-agent --host 0.0.0.0 --multi-user --provider=$PROVIDER & sleep 1"
        done

        for index in $(seq $user); do
            echo "    > Logging $USER_PREFIX$index"
            curl_login $index &
            PIDS="$PIDS $!"
            sleep $SLEEP
        done

        wait $PIDS
        PIDS=""
        echo "  > Killing Pixelated UA"
        run_on_vagrant "pkill pixelated"

        echo
    done
    run_on_vagrant "mv ~/MetricsTime /vagrant/service/test/login/metrics/${user}-users.txt"
    mv load-test.log ../login/metrics/${user}-curl.txt
    echo
done
