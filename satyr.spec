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
Release: 14%{?dist}
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

# git is need for '%%autosetup -S git' which automatically applies all the
# patches above. Please, be aware that the patches must be generated
# by 'git format-patch'
BuildRequires: git

Patch0: satyr-0.13-elfutils-0.158.patch
Patch1: satyr-0.13-elfutils-unwinder.patch
Patch2: satyr-0.13-disable-fingerprints.patch
Patch3: satyr-0.13-unwinder-refresh-config-h.patch

# 1142856, minor bugs found by static analyzer
Patch4: satyr-0.13-static-analyzer-bugs.patch

# 1123262, empty duphash of unreliable koops
Patch5: satyr-0.13-koops-unreliable-frames.patch

# 1142339, python exception parsing
Patch6: satyr-0.13-python-exceptions.patch

# 1142338, ppc64 backtrace parsing
Patch7: satyr-0.13-ppc64-backtrace-parsing.patch

# 1142346, limit stacktrace depth
Patch8: satyr-0.13-limit-stacktrace-depth.patch

# 1139555, ureport auth support
Patch9: satyr-0.13-ureport-auth-support.patch

# 1034857, ignore java suppressed exceptions
Patch10: satyr-0.13-java-suppressed-exceptions.patch

# 1147952, don't free gdb stacktrace on method failure
Patch11: satyr-0.13-dont-free-gdb-stacktrace.patch

# 1142346, better handling of infinite recursion
Patch12: satyr-0.13-better-inf-recursion-handling.patch

# 1210599, add functionality to generate a backtrace without saving a coredump
Patch13: satyr-0.13-fulfill-missing-values-in-core-frames.patch
Patch14: satyr-0.13-unwind-minor-refactoring.patch
Patch15: satyr-0.13-support-unwinding-from-core-hook.patch
Patch16: satyr-0.13-debug-unwinding-from-core-hook-using-satyr-binary.patch
Patch17: satyr-0.13-disable-hook-unwind-on-kernels-w-o-PTRACE_SEIZE.patch
Patch18: satyr-0.13-abrt-refactorize-unwinding-from-core-hook.patch
Patch19: satyr-0.13-core_unwind-fix-the-missing-frame-build_id-and-file.patch

# 1334604, add support for Ruby
Patch20: satyr-0.13-Add-support-for-Ruby-report-type.patch
Patch21: satyr-0.13-python-add-Ruby-support.patch

# 1332869, actualize list of normalization function in satyr
Patch22: satyr-0.13-normalize-extend-xorg-blacklist.patch
Patch23: satyr-0.13-normalization-additional-X-GDK-functions.patch
Patch24: satyr-0.13-normalization-add-glibc-__assert_fail_base.patch
Patch25: satyr-0.13-normalization-add-glibc-__libc_fatal.patch
Patch26: satyr-0.13-normalization-normalize-out-exit-frames.patch
Patch27: satyr-0.13-normalization-actualize-list-of-functions.patch

# 1334604, add support for Ruby testsuite fix
Patch28: satyr-0.13-tests-fix-failure-on-gcc5-on-x86_64.patch

# 1336390, fix defects found by coverity
Patch29: satyr-0.13-Fix-defects-found-by-coverity.patch
Patch30: satyr-0.13-Check-the-return-value-of-sr_parse_char_cspan.patch

# 1342469, support for VARIANT and VARIANT_ID
Patch31: satyr-0.13-os-add-support-for-OS-Variant.patch

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
# http://www.rpm.org/wiki/PackagerDocs/Autosetup
# Default '__scm_apply_git' is 'git apply && git commit' but this workflow
# doesn't allow us to create a new file within a patch, so we have to use
# 'git am' (see /usr/lib/rpm/macros for more details)
%define __scm_apply_git(qp:m:) %{__git} am
%autosetup -S git

%build
autoreconf

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
make check || {
    # find and print the logs of failed test
    # do not cat tests/testsuite.log because it contains a lot of bloat
    find tests -name "testsuite.log" -print -exec cat '{}' \;
    exit 1
}


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
* Mon Jun 06 2016 Matej Habrnal <mhabrnal@redhat.com> - 0.13-14
- add support for OS Variant
  - Related: #1342469

* Thu May 12 2016 Matej Habrnal <mhabrnal@redhat.com> - 0.13-13
- add support for Ruby
  - Related: #1334604
- actualize list of normalization function in satyr
  - Related: #1332869
- fix defects found by coverity
  - Related: #1336390

* Wed Sep 9 2015 Richard Marko <rmarko@redhat.com> - 0.13-12
- apply last patch
  - Related: #1210599

* Wed Sep 9 2015 Richard Marko <rmarko@redhat.com> - 0.13-11
- core unwind: fix the missing frame build_id and file_name
  - Related: #1210599

* Fri Jul 17 2015 Richard Marko <rmarko@redhat.com> - 0.13-10
- leave saving of core backtrace to abrt hook
  - Related: #1210599

* Tue Jun 23 2015 Richard Marko <rmarko@redhat.com> - 0.13-9
- Add functionality to generate a backtrace without saving a coredump
  - Resolves: #1210599

* Wed Nov 19 2014 Martin Milata <mmilata@redhat.com> - 0.13-8
- Better handling of stacktraces with infinite recursion
  - Resolves: #1142346

* Fri Oct 03 2014 Martin Milata <mmilata@redhat.com> - 0.13-7
- Don't free GDB stacktrace on error
  - Resolves: #1147952

* Fri Oct 03 2014 Martin Milata <mmilata@redhat.com> - 0.13-6
- Ignore suppressed exceptions in the Java exception parser
  - Resolves: #1034857

* Thu Sep 18 2014 Martin Milata <mmilata@redhat.com> - 0.13-5
- Fix minor bugs found by static analyzers
  - Resolves: #1142856
- Return empty duphash for koopses with no reliable frames
  - Resolves: #1123262
- Fix parsing of python SyntaxError exceptions
  - Resolves: #1142339
- Fix parsing of ppc64 gdb stacktraces
  - Resolves: #1142338
- Limit the depth of generated stacktrace to avoid huge reports
  - Resolves: #1142346
- Add authentication support to uReport, needed for reporting to customer portal
  - Resolves: #1139555

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
