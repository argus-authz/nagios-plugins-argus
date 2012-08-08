Name: nagios-plugins-argus

Version: 1.0.1
Release: 1%{?dist}
Summary: Nagios plugins for Argus


License: ASL 2.0
Group: System Environment/Libraries
URL: https://twiki.cern.ch/twiki/bin/view/EGEE/AuthorizationFramework

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: python

%description
Nagios plugins for the Argus Authorization Service (EMI)

%prep
%setup

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{_libexecdir}/grid-monitoring/probes/%{name}
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PDP.traffic
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PEP.memory
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PAP.policies
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PDP.status
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PEP.traffic
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PEP.status
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PAP.memory
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PDP.memory
%{_libexecdir}/grid-monitoring/probes/nagios-plugins-argus/nagios-plugins-argus.PAP.status

%dir %{_libexecdir}/grid-monitoring/probes/%{name}/framework
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/__init__.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/AbstractProbe.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/HTTPSHandler.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/MemoryProbe.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/Probe.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/StatusProbe.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/TrafficProbe.py
%{_libexecdir}/grid-monitoring/probes/%{name}/framework/Version.py

%dir /var/lib/grid-monitoring/%{name}

%doc README CHANGELOG

%changelog
* Fri Aug 3 2012 Valery Tschopp <valery.tschopp@switch.ch> 1.0.1-1
- Self managed packaging with spec file.

* Tue Apr 3 2012 Valery Tschopp <valery.tschopp@switch.ch> 1.0.0-1
- Initial Argus Nagios probes for EMI-2.



