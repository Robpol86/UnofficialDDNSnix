Name:       {{NAME}}
Version:    {{VERSION}}
Release:    1%{?dist}
Summary:    {{SUMMARY}}

License:    MIT
URL:        {{URL}}
Source0:    %{name}-%{version}.tar.gz

BuildArch:  noarch
BuildRequires:  python

%description
%{summary}

%prep
%setup -q

%install
rm -rf %{buildroot}
mkdir -p "%{buildroot}%{_datarootdir}/%{name}"  # /usr/share
mkdir -p "%{buildroot}%{_localstatedir}/%{name}"  # /var
mkdir -p "%{buildroot}%{_bindir}"  # /usr/bin
cp -r daemon *.py LICENSE README.md "%{buildroot}%{_datarootdir}/%{name}"
ln -s "%{_datarootdir}/%{name}/%{name}.py" "%{buildroot}%{_bindir}/%{name}"
ln -s "%{name}.py" "%{buildroot}%{_datarootdir}/%{name}/%{name}"

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_datarootdir}/%{name}/daemon/*.py*
%{_datarootdir}/%{name}/daemon/LICENSE*
%{_datarootdir}/%{name}/daemon/ChangeLog
%{_datarootdir}/%{name}/daemon/version/*.py*
%{_datarootdir}/%{name}/*.py*
%{_datarootdir}/%{name}/LICENSE
%{_datarootdir}/%{name}/README.md
%{_bindir}/%{name}
%{_datarootdir}/%{name}/%{name}
%dir %{_localstatedir}/%{name}

%changelog
* Sun Jan 04 2014 Robpol86 <robpol86@gmail.com>
- initial build

