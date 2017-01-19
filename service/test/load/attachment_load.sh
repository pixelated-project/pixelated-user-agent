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

#!/usr/bin/env bash

number=$1
csrf=$2
session=$3

if [ -z $sleep_time ]
then
    sleep_time=0.5
fi

if [ -z $host ]
then
    host='https://unstable.pixelated-project.org:8080'
fi

echo "upload $number files"
echo "with csrf $csrf"
echo "and session $session"
echo "in $host"

echo "Generating $number attachements of 5Mb size..."
for i in `seq 1 $number`; do
    rm -rf /tmp/test$i
    dd if=/dev/urandom of=/tmp/test$i bs=1M count=5
done

new_line=""

echo "Uploading..."
for i in `seq 1 $number`; do
    echo $new_line
    echo "Attachment $i"
    curl -sS -k -X POST --cookie "XSRF-TOKEN=$csrf; TWISTED_SESSION=$session;" \
         --header "X-XSRF-TOKEN=$csrf"  -F attachment=@/tmp/test$i -F csrftoken=$csrf \
         $host/attachment &
    sleep $sleep_time
done

echo $new_line
echo "Done..."

