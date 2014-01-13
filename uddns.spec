Name:       {{NAME}}
Version:    {{VERSION}}
Release:    1%{?dist}
Summary:    {{SUMMARY}}

License:    MIT
URL:        {{URL}}
Source0:    %{name}-%{version}.tar.gz

BuildArch:  noarch
BuildRequires:  python
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
mkdir -p "%{buildroot}%{_datarootdir}/%{name}"  # /usr/share
mkdir -p "%{buildroot}%{_localstatedir}/%{name}"  # /var
mkdir -p "%{buildroot}%{_sysconfdir}"  # /etc
mkdir -p "%{buildroot}%{_bindir}"  # /usr/bin
mkdir -p "%{buildroot}%{_initrddir}"  # /etc/rc.d/init.d
cp -r yaml daemon *.py LICENSE README.md "%{buildroot}%{_datarootdir}/%{name}"
cp UnofficialDDNS.sysvinit.sh "%{buildroot}%{_initrddir}/%{name}"
ln -s "%{_datarootdir}/%{name}/%{name}.py" "%{buildroot}%{_bindir}/%{name}"
ln -s "%{name}.py" "%{buildroot}%{_datarootdir}/%{name}/%{name}"
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
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add %{_initrddir}/%{name}

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{_initrddir}/%{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{_initrddir}/%{name}
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service <script> condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(644,root,root,755)
%dir %{_datarootdir}/%{name}
%dir %{_datarootdir}/%{name}/yaml
%dir %{_datarootdir}/%{name}/daemon
%dir %{_datarootdir}/%{name}/daemon/version
%{_datarootdir}/%{name}/yaml/LICENSE
%{_datarootdir}/%{name}/yaml/README
%{_datarootdir}/%{name}/yaml/CHANGES
%{_datarootdir}/%{name}/daemon/LICENSE*
%{_datarootdir}/%{name}/daemon/ChangeLog
%{_datarootdir}/%{name}/LICENSE
%{_datarootdir}/%{name}/README.md
%{_bindir}/%{name}
%{_datarootdir}/%{name}/%{name}
%config %attr(640,root,uddns) %{_sysconfdir}/%{name}.yaml
%attr(755,root,root) %{_initrddir}/%{name}
%attr(755,root,root) %{_datarootdir}/%{name}/yaml/*.py*
%attr(755,root,root) %{_datarootdir}/%{name}/daemon/*.py*
%attr(755,root,root) %{_datarootdir}/%{name}/daemon/version/*.py*
%attr(755,root,root) %{_datarootdir}/%{name}/*.py*
%dir %attr(755,uddns,uddns) %{_localstatedir}/%{name}

%changelog
* Sun Jan 04 2014 Robpol86 <robpol86@gmail.com>
- initial build

