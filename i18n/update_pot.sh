#!/bin/sh
if [ ! $# -eq 1 ]
then
	echo "Usage: $0 application"
	exit 1
fi
application=$1
if [ ! -d "../applications/$application" ]
then
	echo "../applications/$application not found"
	exit 2
fi
cd ..
xgettext -Lphp common/views/*.html applications/$application/views/*.html \
	-o applications/$application/i18n/messages.pot
