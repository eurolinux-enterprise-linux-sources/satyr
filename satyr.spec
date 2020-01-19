%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# rhel6's python-sphinx cannot build manual pages
%if 0%{?rhel} && 0%{?rhel} <= 6
  %define enable_python_manpage 0
%else
  %define enable_python_manpage 1
%endif

%if 0%{?suse_version}
  %define python2_devel python-devel
  %define libdw_devel libdw-devel
  %define libelf_devel libelf-devel
%else
  %define python2_devel python2-devel
  %define libdw_devel elfutils-devel
  %define libelf_devel elfutils-libelf-devel
%endif

Name: satyr
Version: 0.13
Release: 4%{?dist}
Summary: Tools to create anonymous, machine-friendly problem reports
Group: System Environment/Libraries
License: GPLv2+
URL: https://github.com/abrt/satyr
Source0: https://fedorahosted.org/released/abrt/satyr-%{version}.tar.xz
BuildRequires: %{python2_devel}
BuildRequires: %{libdw_devel}
BuildRequires: %{libelf_devel}
BuildRequires: binutils-devel
BuildRequires: rpm-devel
BuildRequires: libtool
BuildRequires: pkgconfig
BuildRequires: automake
BuildRequires: gcc-c++
%if %{?enable_python_manpage}
BuildRequires: python-sphinx
%endif

Patch0: satyr-0.13-elfutils-0.158.patch
Patch1: satyr-0.13-elfutils-unwinder.patch
Patch2: satyr-0.13-disable-fingerprints.patch
Patch3: satyr-0.13-unwinder-refresh-config-h.patch

%description
Satyr is a library that can be used to create and process microreports.
Microreports consist of structured data suitable to be analyzed in a fully
automated manner, though they do not necessarily contain sufficient information
to fix the underlying problem. The reports are designed not to contain any
potentially sensitive data to eliminate the need for review before submission.
Included is a tool that can create microreports and perform some basic
operations on them.

%package devel
Summary: Development libraries for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development libraries and headers for %{name}.

%package python
Summary: Python bindings for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description python
Python bindings for %{name}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%configure \
%if ! %{?enable_python_manpage}
        --disable-python-manpage \
%endif
        --disable-static

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

# Remove all libtool archives (*.la) from modules directory.
find %{buildroot} -name "*.la" | xargs rm --

%check
make check

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc README NEWS COPYING
%{_bindir}/satyr
%{_mandir}/man1/%{name}.1*
%{_libdir}/lib*.so.*

%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*

%files python
%dir %{python_sitearch}/%{name}
%{python_sitearch}/%{name}/*

%if %{?enable_python_manpage}
%{_mandir}/man3/satyr-python.3*
%endif

%changelog
* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.13-4
- Mass rebuild 2014-01-24

* Wed Jan 22 2014 Martin Milata <mmilata@redhat.com> 0.13-3
- Fix build with elfutils unwinder
  - Resolves: #1051569

* Tue Jan 14 2014 Martin Milata <mmilata@redhat.com> 0.13-2
- Use elfutils unwinder
  - Resolves: #1051569
- Disable function fingerprinting
  - Resolves: #1052402

* Tue Jan 07 2014 Martin Milata <mmilata@redhat.com> 0.13-1
- Rebase to satyr-0.13
  - Resolves: #1040900
- Includes patch to build against elfutils-0.158

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.9-3
- Mass rebuild 2013-12-27

* Wed Dec 04 2013 Martin Milata <mmilata@redhat.com> 0.9-2
- Fix malformed JSON for some Java and koops reports
  - Resolves: #1035317
  - Resolves: #1036790
- Fix memory leak in RPM handling
  - Resolves: #1016780
- Check for unsigned overflows
  - Resolves: #1034869

* Wed Sep 11 2013 Jakub Filak <jfilak@redhat.com> 0.9-1
- New upstream version
  - Enrich koops uReport data with koops text and kernel version.
  - Improve koops modules handling.

* Wed Aug 28 2013 Richard Marko<rmarko@redhat.com> 0.8-1
- New upstream version
  - Added support for json de/serialization of reports and stacktraces.
  - Library version number increased, as the interface changed since the last release

* Mon Aug 26 2013 Martin Milata <mmilata@redhat.com> 0.7-1
- New upstream version
  - Fix couple of crashes (#997076, #994747)

* Mon Jul 29 2013 Martin Milata <mmilata@redhat.com> 0.6-1
- New upstream version
  - Do not export internal function symbols.

* Thu Jul 25 2013 Martin Milata <mmilata@redhat.com> 0.5-2
- Remove libunwind dependency altogether, always use GDB for unwinding.

* Thu Jul 25 2013 Jakub Filak <jfilak@redhat.com> 0.5-1
- Added function that creates core stacktrace from GDB output. Several bugfixes.

* Tue Jul 09 2013 Martin Milata <mmilata@redhat.com> 0.4-2
- Fix failing tests (failure manifests only on s390x)

* Mon Jul 08 2013 Martin Milata <mmilata@redhat.com> 0.4-1
- New upstream version
  - Added features needed by ABRT
  - Support for uReport2
  - Major C and Python API changes
- Patch for python-2.6 compatibility

* Tue Apr 02 2013 Dan Horák <dan[at]danny.cz> 0.3-2
- libunwind exists only on selected arches

* Mon Mar 25 2013 Martin Milata <mmilata@redhat.com> 0.3-1
- New upstream version
  - Bug fixes
  - Build fixes for older systems
- Do not require libunwind on rhel

* Mon Mar 18 2013 Martin Milata <mmilata@redhat.com> 0.2-1
- Documentation and spec cleanup
- Build fixes (build against RPM)

* Mon Aug 30 2010 Karel Klic <kklic@redhat.com> 0.1-1
- Upstream package spec file
