Summary: A dynamic adaptive system tuning daemon
Name: tuned
Version: 0.2.11
Release: 8%{?dist}
License: GPLv2+
Group: System Environment/Daemons
# The source for this package was pulled from upstream git.  Use the
# following commands to get the corresponding tarball:
#  git clone git://git.fedorahosted.org/git/tuned.git
#  cd tuned
#  git checkout v%{version}
#  make archive
Source: tuned-%{version}.tar.bz2
Patch1: tuned-nettool-interface.patch
Patch2: tuned-sysctl-unknown-key.patch
Patch3: tuned-remove-sysctl-ktune.patch 
Patch4: tuned-remove-spindown-profile.patch
Patch5: tuned-adm-safe-profiles.patch
Patch6: tuned-profiles-update-0.2.15.patch
Patch7: tuned-install.patch
Patch8: tuned-nettool-supported_modes.patch
Patch9: tuned-check-before-you-jump.patch
Patch10: tuned-enterprise-storage-profile.patch
URL: https://fedorahosted.org/tuned/
Buildroot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: python
Requires: usermode ethtool
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
BuildArch: noarch

%description
The tuned package contains a daemon that tunes system settings dynamically.
It does so by monitoring the usage of several system components periodically.
Based on that information components will then be put into lower or higher
power saving modes to adapt to the current usage. Currently only ethernet
network and ATA harddisk devices are implemented.

%package utils
Summary: Disk and net statistic monitoring systemtap scripts
Requires: systemtap
Group: Applications/System

%description utils
The tuned-utils package contains several systemtap scripts to allow detailed
manual monitoring of the system. Instead of the typical IO/sec it collects
minimal, maximal and average time between operations to be able to
identify applications that behave power inefficient (many small operations
instead of fewer large ones).

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1

%build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# fix profile scripts permissions
chmod a+x %{buildroot}/etc/tune-profiles/*/ktune.sh

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add tuned
/sbin/chkconfig --add ktune

%preun
if [ $1 = 0 ] ; then
    /sbin/service tuned stop >/dev/null 2>&1
    /sbin/chkconfig --del tuned
    /sbin/service ktune stop >/dev/null 2>&1
    /sbin/chkconfig --del ktune
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service tuned condrestart >/dev/null 2>&1 || :
    /sbin/service ktune condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING INSTALL NEWS README doc/DESIGN.txt doc/TIPS.txt ktune/README.ktune doc/examples
%{_initddir}/tuned
%config(noreplace) %{_sysconfdir}/tuned.conf
%config(noreplace) %{_sysconfdir}/pam.d/tuned-adm
%config(noreplace) %{_sysconfdir}/security/console.apps/tuned-adm
%{_sbindir}/tuned
%{_sbindir}/tuned-adm
# consolehelper hard link
%{_bindir}/tuned-adm
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/tune-profiles/active-profile
%{_sysconfdir}/tune-profiles
%{_datadir}/tuned
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%attr(0755,root,root) %{_initddir}/ktune
%config(noreplace) %{_sysconfdir}/sysconfig/ktune
%config(noreplace) %{_sysconfdir}/ktune.d/tunedadm.conf
%dir %attr(0755,root,root) %{_sysconfdir}/ktune.d
%dir /var/log/tuned
%dir /var/run/tuned

%files utils
%defattr(-,root,root,-)
%doc doc/README.utils
%doc doc/README.scomes
%{_sbindir}/varnetload
%{_sbindir}/netdevstat
%{_sbindir}/diskdevstat
%{_sbindir}/scomes


%changelog
* Tue Aug 17 2010 Jarod Wilson <jarod@redhat.com> 0.2.11-8
- Don't touch transparent hugepage or cpufreq settings if not supported (#621877)
- Add new enterprise-storage profile based on throughput-performance:
  * Disables barriers for all non-root non-/boot file systems (#624736)
  * Increases the default readahead value from 128kb to 512kb (#624828)

* Tue Aug 03 2010 Phil Knirsch <pknirsch@redhat.com> 0.2.11-7
- Fixes #620686 - Problem with network cards that provide unparsable supported network modes

* Wed Jul 14 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-6
- Jarod Wilson: profiles update (#604046, #587432)
- fresh installation and SELinux fixes

* Thu Jun 17 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-5
- Fixes #605217 - tuned-adm unsafe profiles loading
  tuned-adm tool updated to the newest upstream version

* Thu May 27 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-4
- Fixes #596817 - spindown-disk profile requires hciconfig
  problematic profile was completely removed

* Thu May 06 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-3
- Fixes #577971 - error: "net.bridge.bridge-nf-call-ip6tables" is an unknown key (Thomas Woerner)
- Fixes #588739 - tuned should not apply /etc/sysctl.ktune settings (Jan Vcelak)

* Tue Mar 30 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-2
- Fixes: #578104

* Mon Mar 22 2010 Phil Knirsch <pknirsch@redhat.com> 0.2.11-1
- Added support for display of currently active profile
- Fix missing help command
- Large update to documentation and manpages
- Updated several of the profiles
- Updated ALPM powersave code in the various powersave profiles
- Disabled USB autosuspend in laptop-battery-powersave for now

* Wed Feb 03 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.10-1
- Log file moved to separate directory.

* Mon Feb 01 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.9-1
- New release.

* Tue Jan 26 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.8-2
- Included Thomas Woerner's patch checking user rights when executing
  ktune service commands.
- Included Jan Vcelak's patch fixing logging module initialization.

* Fri Jan 08 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.8-1
- New release. Adds logging support.

* Mon Dec 21 2009 Jan Vcelak <jvcelak@redhat.com> 0.2.7-2
- Fixed 542305 - [abrt] crash detected in tuned-0.2.5-2.fc12
  Some ethernet cards are not supported by 'ethtool'.

* Fri Dec 11 2009 Thomas Woerner <twoerner@redhat.com> 0.2.7-1
- Updated ktune to version 0.4-1
  - Supports start and stop options in profile scripts calls
  - Fixed CMDLINE_ELEVATOR test (rhbz#496940#c9)

* Tue Dec 08 2009 Phil Knirsch <pknirsch@redhat.com> 0.2.6-1
- Included Jan Vcelak's patch for pyo and pyc files
- Updated ktune.sh script for laptop-battery-powersave profile with latest
  ALPM mechanism
- Fixed ktune.sh script for laptop-battery-powersave profile to stop printing
  errors when files in /sys are missing

* Thu Nov 26 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.5-2
- Added python into build requires
- Resolves: #539949

* Tue Nov 03 2009 Phil Knirsch <pknirsch@redhat.com> 0.2.5-1
- Moved from prerelease to normal
- Added missing ethtool requires
- Fixed 532209 - init priority wrong for ktune (Jan Vcelak)
- Fixed 530457 - [abrt] crash detected in tuned-0.2.5-0.1.fc12 (Jan Vcelak)
- Added detection of netcard supported speeds (Jan Vcelak)
- Fix ktune.sh script for stopping in regard to ALPM and CDROM polling (Phil Knirsch)

* Mon Oct 19 2009 Marcela Mašláňová <mmaslano@redhat.com> 0.2.5-0.3
- new release

* Thu Oct 15 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.5-0.2
- Allow run tuned-adm as root for users at the physical console

* Mon Oct 12 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.5-0.1
- Removed dependence on kobo
- Bumped to 0.2.5 pre release version

* Wed Sep 23 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.4-2
- fixed url to fedorahosted project page
- Resolves: #519019

* Mon Sep 21 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.4-1
- Update release to tuned-0.2.4
- Resolves: #523385

* Tue Aug 18 2009 Phil Knirsch <pknirsch@redhat.com> 0.2.3-1
- Updated documentation
- Few more fixes for tuned-adm

* Fri Aug 14 2009 Phil Knirsch <pknirsch@redhat.com>  0.2.2-1
- Updates to the ktune scripts
- Added support for start/stop of the ktune scripts and ktune initscript

* Tue Aug 04 2009 Phil Knirsch <pknirsch@redhat.com> - 0.2.1-1
- Added first set of profiles
- Added tuned-adm tool for profile switching
- Fixed several issues with the tuned-adm tool

* Mon Jul 27 2009 Thomas Woerner <twoerner@redhat.com> - 0.2.0-1
- Integrated ktune-0.4

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.7-1
- Added first version CPU tuning and monitoring plugins

* Thu Jun 25 2009 Petr Lautrbach <plautrba@redhat.com> - 0.1.6-1
- added scomes

* Wed Mar 25 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.5-1
- Updated documentation, thanks to Marcela Maslanova!
- Updated diskdevstat and netdevstat to have command line arguments
- Added the possibility to output a histogram at the end of the
  run for detailed information about the collected data

* Fri Mar 06 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.4-1
- Dropped unecessary kernel-debuginfo requires from tuned-utils

* Mon Mar 02 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.3-1
- Fixed placement of doc entry at tuned-utils package

* Thu Feb 26 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.2-1
- Added config file option to enable/disable plugins
- Switched from ConfigParser to RawConfigParser
- Renamed doc/README.txt to doc/DESIGN.txt
- Added tuned.conf man page
- Updated tuned man page
- Updated package descriptions (#487312)
- Added documentation for utils scripts (#487312)

* Wed Feb 25 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.1-1
- Bump version
- Added comment in empty __init__.py files
- Fixed BuildRoot tag to use latest recommendation of FPG
- Lots of whitespace changes
- Some minor README changes
- Added a changelog rule in Makefile
- Fixed rpmlint error messages
- Add init() methods to each plugin
- Call plugin init() methods during tuned's init()
- Add support for command line parameters
      o -c conffile|--config==conffile to specify the location of the config file
      o -d to start tuned as a daemon (instead of as normal app)
- Readded the debug output in case tuned isn't started as as daemon
- Fixed initialization of max transfer values for net tuning plugin
- Added complete cleanup code in case of tuned exiting and/or
  getting a SIGTERM to restore default values
- Made the disk tuning pluging less nosy if started as non-daemon
- Fixed missing self. in the tuned.py config handling
- Added a manpage
- Fixed summary
- Added missing GPL notic to tuned.py
- Added explanation for Source entry in specfile
- Added a distarchive target for the Makefile for proper tagging in git
- Added a explanation how to create the tarball via git in the specfile
- Fixed the defattr() lines in the specfile to conform FRG

* Mon Feb 23 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.0-1
- Initial version
