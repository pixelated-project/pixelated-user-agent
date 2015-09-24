#!/usr/bin/env bash

TEMPLATE_FILE="app/js/generated/hbs/templates.js"

COMMITISH=$(git rev-parse --short HEAD)

perl -pi -e "s/UNKNOWN_VERSION/$COMMITISH/" $TEMPLATE_FILE

if [ ! -f "$TEMPLATE_FILE" ] ; then
    echo "file $TEMPLATE_FILE not found" 1>&2
    exit 1
fi

exit 0
