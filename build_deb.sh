#!/bin/bash

##############################################################################
# MIT License
# Copyright (c) 2014 Robpol86
##############################################################################

set -e

NAME=UnofficialDDNS
VERSION=$(./$NAME.py --version)
SUMMARY=$(./$NAME.py --help |head -1)
URL=$(./$NAME.py --help |head -2 |tail -1)
SOURCE="$HOME/debbuild"

# Build directory structure.
[ -d $SOURCE ] && rm -rf $SOURCE
mkdir -p $SOURCE/DEBIAN $SOURCE/etc/init.d $SOURCE/var/$NAME
mkdir -p $SOURCE/usr/share/$NAME

# Copy main files.
cp -r yaml daemon *.py LICENSE README.md $SOURCE/usr/share/$NAME
cp UnofficialDDNS.lsbinit.sh $SOURCE/etc/init.d/$NAME
cp control $SOURCE/DEBIAN
ln -s $NAME.py $SOURCE/usr/share/$NAME/$NAME
python -m compileall $SOURCE/usr/share/$NAME > /dev/null
python -O -m compileall $SOURCE/usr/share/$NAME > /dev/null

# Generate config file.
cat > $SOURCE/etc/$NAME.yaml << EOF
log:    /var/$NAME/$NAME.log
pid:    /var/$NAME/$NAME.pid
daemon: True
#verbose: True
user:   myuser #replace me
passwd: mypassword #replace me
domain: server.yourdomain.com #replace me
EOF
echo "/etc/UnofficialDDNS.yaml" > $SOURCE/DEBIAN/conffiles

# Generate md5sums.
(cd $SOURCE && \
    find . -type f ! -regex '.*?DEBIAN.*' -printf '%P ' |xargs md5sum) > \
    $SOURCE/DEBIAN/md5sums

# Generate postinst.
cat > $SOURCE/DEBIAN/postinst << EOF
#!/bin/sh
update-rc.d -f $NAME defaults
getent group uddns >/dev/null || groupadd -r uddns
getent passwd uddns >/dev/null || \
    useradd -r -g uddns -d /var/$NAME -s /sbin/nologin \
    -c "Service account for $NAME" uddns
chown -R uddns:uddns /var/$NAME
chown root:uddns /etc/$NAME.yaml
exit 0
EOF

# Generate preinst.
cat > $SOURCE/DEBIAN/preinst << EOF
#!/bin/sh
[ -f /etc/init.d/$NAME ] && /usr/sbin/service $NAME stop
exit 0
EOF

# Generate prerm.
cat > $SOURCE/DEBIAN/prerm << EOF
#!/bin/sh
/usr/sbin/service $NAME stop
[ "\$1" = "remove" ] && update-rc.d -f $NAME remove
exit 0
EOF

# Set permissions.
chmod 640 $SOURCE/etc/$NAME.yaml
chmod 755 $SOURCE/DEBIAN/postinst $SOURCE/DEBIAN/prerm $SOURCE/etc/init.d/$NAME
find $SOURCE -type f -name \*.py\* -printf '%p ' |xargs chmod 755

# Replace placeholders.
SIZE=$(du -kc $SOURCE/{etc,usr,var} |tail -1 |cut -f1)
sed -i "s/{{NAME}}/$NAME/" $SOURCE/DEBIAN/control
sed -i "s/{{VERSION}}/$VERSION/" $SOURCE/DEBIAN/control
sed -i "s/{{SUMMARY}}/$SUMMARY/" $SOURCE/DEBIAN/control
sed -i "s/{{SIZE}}/$SIZE/" $SOURCE/DEBIAN/control
sed -i "s/{{SUMMARY}}/$SUMMARY/" $SOURCE/etc/init.d/$NAME
sed -i "s|{{URL}}|$URL|" $SOURCE/etc/init.d/$NAME

# Build
dpkg -b $SOURCE ${NAME,,}_${VERSION}_all.deb
