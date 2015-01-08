%define debug_package %{nil}

Name: grub-efi
Version: 0.97
Release: 10
Summary: Grand Unified Boot Loader
Group: System/Kernel and hardware
License: GPLv2+

ExclusiveArch: x86_64 %ix86
BuildRequires: binutils >= 2.9.1.0.23, ncurses-devel, ncurses, texinfo
BuildRequires: autoconf automake
BuildRequires: gnu-efi >= 3.0e-9
BuildRequires: glibc glibc-static-devel
BuildRequires: git
Requires: coreutils
Provides: bootloader

URL: http://www.gnu.org/software/%{name}/
Source0: ftp://alpha.gnu.org/gnu/%{name}/%{name}-%{version}.tar.gz

# *** FIXME *** THIS IS EVIL
# There is a problem in the grub-legacy codebase that prevents it
# from working when built with a modern toolchain, even at -O0.
# So for now, we'll overwrite grub.efi with a binary compiled with
# a known old enough toolchain.
# The source used is the exact same source found in this package.
# Binaries are extracted from
# http://abf-downloads.rosalinux.ru/rosa2012.1/repository/x86_64/main/release/grub-efi-0.97-94-rosa2012.1.x86_64.rpm
# http://abf-downloads.rosalinux.ru/rosa2012.1/repository/i586/main/release/grub-efi-0.97-94-rosa2012.1.i586.rpm
Source100: grub-x86_64.efi
Source101: grub-x86_32.efi

# This is from
# http://git.kernel.org/?p=boot/grub-fedora/grub-fedora.git;a=summary
Patch0: grub-fedora-17.patch
Patch1: 0001-Fix-strange-compilation-problem.patch
Patch2: 0003-Move_network-disable-earlier.patch
Patch3: 0004-Make-sure-align-is-initialised.patch
Patch4: 0005-Fix-Apple-CD-fixup.patch
Patch5: 0006-Avoid-broken-uefi-fs.patch
Patch6: 0007-fix-uefi-stride.patch
Patch7: 0008-fix-gop.patch
Patch100: grub-efi-0.97-automake.patch
Patch101: grub-efi-0.97-stdint.patch

%description
GRUB (Grand Unified Boot Loader) is an experimental boot loader
capable of booting into most free operating systems - Linux, FreeBSD,
NetBSD, GNU Mach, and others as well as most commercial operating
systems.

%package efi
Summary: GRUB bootloader for EFI systems
Group: System/Kernel and hardware

%description efi
GRUB for EFI systems is a bootloader used to boot EFI systems.

%prep
%setup -q
#git init
#git config user.email "pjones@fedoraproject.org"
#git config user.name "Fedora Ninjas"
#git add .
#git commit -a -q -m "%{version} baseline."
#git am %{patches}

# Modify grub to show the full version number
#sed -i 's/0\.97/%{version}-%{release}/' configure.in

%apply_patches

%build
aclocal ; autoheader ; automake -a ; autoconf

#needs gnu as for a start
export CC=gcc
export CXX=g++

GCCVERS=$(gcc --version | head -1 | cut -d\  -f3 | cut -d. -f1)
CFLAGS="-O2 -fpic -g -fno-strict-aliasing -fno-stack-protector -fshort-wchar -ffreestanding -DGNU_EFI_USE_MS_ABI --std=gnu11 -Wl,--build-id=none -Wall -fuse-ld=bfd -Wl,--hash-style=sysv"
%ifarch x86_64
CFLAGS="$CFLAGS -mno-red-zone -mno-mmx"
%endif
%ifarch %ix86
CFLAGS="$CFLAGS -mno-mmx -mno-sse"
%endif
if [ "$GCCVERS" == "4" ]; then
	CFLAGS="$CFLAGS -Wno-pointer-sign"
fi
export CFLAGS
%configure --sbindir=/sbin --disable-auto-linux-mem-opt --datarootdir=%{_datadir} --with-platform=efi
make

%install
%makeinstall sbindir=${RPM_BUILD_ROOT}/sbin
mkdir -p ${RPM_BUILD_ROOT}/boot/grub
mkdir -m 0755 -p ${RPM_BUILD_ROOT}/boot/efi/EFI/omdv/
%ifarch x86_64
install -c -m 755 %{SOURCE100} ${RPM_BUILD_ROOT}/boot/efi/EFI/omdv/grub.efi
%else
%ifarch %ix86
install -c -m 755 %{SOURCE101} ${RPM_BUILD_ROOT}/boot/efi/EFI/omdv/grub.efi
%else
install -m 755 efi/grub.efi ${RPM_BUILD_ROOT}/boot/efi/EFI/omdv/grub.efi
%endif
%endif

rm -f ${RPM_BUILD_ROOT}/%{_infodir}/dir

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog NEWS README COPYING TODO docs/menu.lst
/boot/grub
/sbin/grub-terminfo
/sbin/grub-md5-crypt
/sbin/grub-crypt
%{_infodir}/grub*
%{_infodir}/multiboot*
%{_mandir}/man*/*
%{_datadir}/grub

%files efi
%defattr(-,root,root)
%attr(0755,root,root)/boot/efi/EFI/omdv

%changelog
* Fri Apr 27 2012 Matthew Garrett <mjg@redhat.com> - 0.97-93
- Fix CD booting on Apples
- Work around Apple firmware bug that hangs in uefi filesystem reads
- Really properly fix Apple framebuffers
- Use the GOP mode the firmware gave us to avoid problems with Intel's driver
