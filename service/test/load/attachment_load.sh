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

