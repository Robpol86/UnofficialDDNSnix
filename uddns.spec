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
cp -r daemon *.py LICENSE README.md "%{buildroot}%{_datarootdir}/%{name}"
ln -s "%{_datarootdir}/%{name}/%{name}.py" "%{buildroot}%{_bindir}/%{name}"
ln -s "%{name}.py" "%{buildroot}%{_datarootdir}/%{name}/%{name}"
cat << EOF > "%{buildroot}%{_sysconfdir}/%{name}.conf"
daemon  True
log     %{_localstatedir}/%{name}/%{name}.log
domain  server.yourdomain.com #replace me
user    myuser #replace me
passwd  mypassword #replace me
EOF

%clean
rm -rf %{buildroot}

%pre
getent group uddns >/dev/null || groupadd -r uddns
getent passwd uddns >/dev/null || \
    useradd -r -g uddns -d %{_localstatedir}/%{name} -s /sbin/nologin \
    -c "Service account for %{name}" uddns
exit 0

%files
%defattr(644,root,root,755)
%{_datarootdir}/%{name}/daemon/LICENSE*
%{_datarootdir}/%{name}/daemon/ChangeLog
%{_datarootdir}/%{name}/LICENSE
%{_datarootdir}/%{name}/README.md
%{_bindir}/%{name}
%{_datarootdir}/%{name}/%{name}
%{_sysconfdir}/%{name}.conf
%attr(755,root,root) %{_datarootdir}/%{name}/daemon/*.py*
%attr(755,root,root) %{_datarootdir}/%{name}/daemon/version/*.py*
%attr(755,root,root) %{_datarootdir}/%{name}/*.py*
%dir %attr(755,uddns,uddns) %{_localstatedir}/%{name}

%changelog
* Sun Jan 04 2014 Robpol86 <robpol86@gmail.com>
- initial build

