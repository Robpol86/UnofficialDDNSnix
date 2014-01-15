#!/bin/bash

##############################################################################
# Source: http://tecadmin.net/create-rpm-of-your-own-script-in-centosredhat/
#
# I assume you've already ran rpmdev-setuptree.
#
# MIT License
# Copyright (c) 2014 Robpol86
##############################################################################

set -e
export PYTHONDONTWRITEBYTECODE=True

NAME=UnofficialDDNS
VERSION=$(./$NAME.py --version)
SUMMARY=$(./$NAME.py --help |head -1)
URL=$(./$NAME.py --help |head -2 |tail -1)
SOURCE="$HOME/rpmbuild/SOURCES/$NAME-$VERSION"
TARFILE=$NAME-$VERSION.tar.gz

# Copy files.
[ -d $SOURCE ] && rm -rf $SOURCE
mkdir $SOURCE
cp -r yaml daemon *.py *.sh LICENSE README.md uddns.spec $SOURCE

# Replace placeholders.
sed -i "s/{{NAME}}/$NAME/" $SOURCE/uddns.spec
sed -i "s/{{VERSION}}/$VERSION/" $SOURCE/uddns.spec
sed -i "s/{{SUMMARY}}/$SUMMARY/" $SOURCE/uddns.spec
sed -i "s|{{URL}}|$URL|" $SOURCE/uddns.spec
sed -i "s/{{SUMMARY}}/$SUMMARY/" $SOURCE/UnofficialDDNS.sysvinit.sh
sed -i "s|{{URL}}|$URL|" $SOURCE/UnofficialDDNS.sysvinit.sh

# Create tarball.
(cd $SOURCE/.. && tar -czhf "$TARFILE" "$NAME-$VERSION")

# Build
rpmbuild -ba $SOURCE/uddns.spec
