%define		plugin	check_ftp_login
Summary:	Nagios plugin to check FTP login and file list
Summary(pl.UTF-8):	Wtyczka Nagiosa sprawdzająca logowanie i listowanie plików na FTP
Name:		nagios-plugin-%{plugin}
Version:	0.1
Release:	1
License:	GPL v2+
Group:		Networking
Source0:	check_ftp_login.py
Source1:	%{plugin}.cfg
Requires:	python3-nagiosplugin
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios/plugins
%define		nrpeddir	/etc/nagios/nrpe.d
%define		plugindir	%{_prefix}/lib/nagios/plugins

%description
Nagios plugin to check FTP login and file list. Supports TLS
connections.

%prep
%setup -qcT
cp -p %{SOURCE0} %{plugin}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{plugindir}}
install -p %{plugin} $RPM_BUILD_ROOT%{plugindir}/%{plugin}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{plugin}.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{plugin}.cfg
%attr(755,root,root) %{plugindir}/%{plugin}
