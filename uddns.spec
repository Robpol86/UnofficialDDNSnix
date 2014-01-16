Name:       {{NAME}}
Version:    {{VERSION}}
Release:    1%{?dist}
Summary:    {{SUMMARY}}
Group:      System Environment/Daemons

License:    MIT
URL:        {{URL}}
Source0:    %{name}-%{version}.tar.gz

BuildArch: noarch
BuildRequires: /usr/bin/python2.6
Requires: /usr/bin/python2.6
Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

%description
%{summary}

%prep
%setup -q

%install
rm -rf %{buildroot}
mkdir -p "%{buildroot}/usr/share/%{name}"  # /usr/share
mkdir -p "%{buildroot}%{_localstatedir}/%{name}"  # /var
mkdir -p "%{buildroot}%{_sysconfdir}"  # /etc
mkdir -p "%{buildroot}/etc/rc.d/init.d"  # /etc/rc.d/init.d
cp -r yaml daemon *.py LICENSE README.md "%{buildroot}/usr/share/%{name}"
cp UnofficialDDNS.sysvinit.sh "%{buildroot}/etc/rc.d/init.d/%{name}"
ln -s "%{name}.py" "%{buildroot}/usr/share/%{name}/%{name}"
cat << EOF > "%{buildroot}%{_sysconfdir}/%{name}.yaml"
log:    %{_localstatedir}/%{name}/%{name}.log
pid:    %{_localstatedir}/%{name}/%{name}.pid
daemon: True
#verbose: True
user:   myuser #replace me
passwd: mypassword #replace me
domain: server.yourdomain.com #replace me
EOF

%clean
rm -rf %{buildroot}

%pre
getent group uddns >/dev/null || groupadd -r uddns
getent passwd uddns >/dev/null || \
    useradd -r -g uddns -d %{_localstatedir}/%{name} -s /sbin/nologin \
    -c "Service account for %{name}" uddns
exit 0

%post
/sbin/chkconfig --add /etc/rc.d/init.d/%{name}
/sbin/chkconfig %{name} off
exit 0

%preun
/sbin/service %{name} status >/dev/null 2>&1
if [ $? -eq 0 ]; then
    # Installed and running.
    /sbin/service %{name} stop
fi
if [ $1 -eq 0 ]; then
    # Only for uninstall, not upgrades.
    /sbin/chkconfig --del /etc/rc.d/init.d/%{name}
fi
exit 0

%files
%defattr(644,root,root,755)
%dir /usr/share/%{name}
%dir /usr/share/%{name}/yaml
%dir /usr/share/%{name}/daemon
%dir /usr/share/%{name}/daemon/version
/usr/share/%{name}/yaml/LICENSE
/usr/share/%{name}/yaml/README
/usr/share/%{name}/yaml/CHANGES
/usr/share/%{name}/daemon/LICENSE*
/usr/share/%{name}/daemon/ChangeLog
/usr/share/%{name}/LICENSE
/usr/share/%{name}/README.md
/usr/share/%{name}/%{name}
%config %attr(640,root,uddns) %{_sysconfdir}/%{name}.yaml
%attr(755,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) /usr/share/%{name}/yaml/*.py*
%attr(755,root,root) /usr/share/%{name}/daemon/*.py*
%attr(755,root,root) /usr/share/%{name}/daemon/version/*.py*
%attr(755,root,root) /usr/share/%{name}/*.py*
%dir %attr(755,uddns,uddns) %{_localstatedir}/%{name}

%changelog
* Sun Jan 15 2014 Robpol86 <robpol86@gmail.com>
- initial build

