#!/bin/sh
releases=$(cat /etc/apt-portal/active_releases)
for release in $releases
do
  cat $HOME/etc/mysql_uri | debfactory/bin/apt2sql.py -mfq -dstdin http://archive.getdeb.net/ubuntu $release-getdeb-testing games
  cat $HOME/etc/mysql_uri | debfactory/bin/apt2sql.py -mfq -dstdin http://archive.getdeb.net/ubuntu $release-getdeb games
done
