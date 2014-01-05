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
SOURCES="$HOME/rpmbuild/SOURCES"
TARFILE=$NAME-$VERSION.tar.gz

# Replace placeholders in spec file.
sed -i "s/{{NAME}}/$NAME/" uddns.spec
sed -i "s/{{VERSION}}/$VERSION/" uddns.spec
sed -i "s/{{SUMMARY}}/$SUMMARY/" uddns.spec
sed -i "s|{{URL}}|$URL|" uddns.spec

# Create tarball.
[ ! -e "$SOURCES/$NAME-$VERSION" ] && ln -s "$(pwd)" "$SOURCES/$NAME-$VERSION"
tar -C "$SOURCES" -czhf "$SOURCES/$TARFILE" --exclude='.git*' "$NAME-$VERSION"

# Build
rpmbuild -ba uddns.spec
