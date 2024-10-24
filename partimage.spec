Summary:	Partition Image
Name:		partimage
Version:	0.6.9
Release:	15
License:	GPLv2
Group:		Archiving/Backup
Url:		https://www.partimage.org/
Source0:	%{name}-%{version}.tar.bz2
Source1:	partimage.1
Source2:	partimaged.8
Source3:	partimagedusers.5
Source4:	partimaged-sysconfig
Source5:	partimaged-init.d
Patch0:		partimage-automake-1.13.patch
Patch1:		partimage-0.6.9-compile.patch
Patch3:		partimage-0.6.7-ssl-certs-policy.patch
Patch13:	partimage-0.6.7-splash.patch
Patch14:	partimage-0.6.9-dereference-gzFile-pointer.patch
Patch15:	partimage-0.6.9-lzma.patch
Patch17:        partimage-0.6.9-no-sslv2.patch
# from debian: fix build config with openssl 1.1
Patch18:        03-openssl11.patch
Patch19:        partimage-0.6.9-sysmacros.patch

BuildRequires:	pkgconfig(bzip2)
BuildRequires:	gettext-devel
#BuildRequires:	slang-static-devel
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(libnewt)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)
Requires:	openssl > 0.9.6

%description
Partition Image is a Linux/UNIX partition imaging utility: it saves
partitions in the following file system formats to an image file:
- Ext2FS & Ext3FS (the linux standard),
- FAT16/32 (DOS & Windows file systems),
- HFS (MacOS File System),
- JFS (Journalised File System, from IBM, used on Aix),
- NTFS (Windows NT File System),
- HPFS (IBM OS/2 File System),
- ReiserFS (a journalized and powerful file system),
- UFS (Unix File System),
- XFS (another jounalized and efficient File System, from SGI, used on Irix),

Only used blocks are copied. The image file can be 
compressed in the GZIP/BZIP2 formats to save disk space, and splitted 
into multiple files to be copied on amovibles floppies (ZIP for example),
or burned on a CD-R ...

This allows to save a full Linux/Windows system, with an only 
operation. When problems (viruses, crash, error, ...), you just have to 
restore, and after several minutes, all your system is restored (boot, 
files, ...), and fully working.

This is very useful when installing the same software on many 
machines: just install one of them, creat|e an image, and just restore 
the image on all other machines. Then, after the first one, each 
installation is automatically made, and only require a few minutes.

%if %{with uclibc}
%package -n	uclibc-%{name}
Summary:	Partition Image (uClibc build)
Group:		Archiving/Backup

%description -n	uclibc-%{name}
Partition Image is a Linux/UNIX partition imaging utility: it saves
partitions in the following file system formats to an image file:
- Ext2FS & Ext3FS (the linux standard),
- FAT16/32 (DOS & Windows file systems),
- HFS (MacOS File System),
- JFS (Journalised File System, from IBM, used on Aix),
- NTFS (Windows NT File System),
- HPFS (IBM OS/2 File System),
- ReiserFS (a journalized and powerful file system),
- UFS (Unix File System),
- XFS (another jounalized and efficient File System, from SGI, used on Irix),

Only used blocks are copied. The image file can be 
compressed in the GZIP/BZIP2 formats to save disk space, and splitted 
into multiple files to be copied on amovibles floppies (ZIP for example),
or burned on a CD-R ...

This allows to save a full Linux/Windows system, with an only 
operation. When problems (viruses, crash, error, ...), you just have to 
restore, and after several minutes, all your system is restored (boot, 
files, ...), and fully working.

This is very useful when installing the same software on many 
machines: just install one of them, creat|e an image, and just restore 
the image on all other machines. Then, after the first one, each 
installation is automatically made, and only require a few minutes.
%endif

%prep
%autosetup -p1
autoreconf -fi

%build
%global build_cxxflags %{build_cxxflags} -std=gnu++11
%configure
%make_build

%install
%make_install

install -m644 %{SOURCE1} -D %{buildroot}%{_mandir}/man1/partimage.1
install -m644 %{SOURCE2} -D %{buildroot}%{_mandir}/man8/partimaged.8
install -m644 %{SOURCE3} -D %{buildroot}%{_mandir}/man5/partimagedusers.5
install -m644 %{SOURCE4} -D %{buildroot}%{_sysconfdir}/sysconfig/partimaged
install -m755 %{SOURCE5} -D %{buildroot}%{_initrddir}/partimaged

cat > README.omv <<EOF
OpenMandriva RPM specific notes

setup
-----
In order to comply with Mandriva SSL certificates policy, partimage binary has
been modified to use the following files:
- /etc/pki/tls/certs/partimage.pem instead of default
  /etc/partimaged/partimaged.cert
- /etc/pki/tls/private/partimage.pem instead of default
  /etc/partimaged/partimaged.key
EOF

%find_lang %{name}

mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/%{name}.conf <<EOF
g partimag - -
u partimag - "Partimag" %{_localstatedir}/lib/partimag /bin/bash
EOF

%post
dir=/var/lib/partimage
if [ ! -d $dir ]; then 
    mkdir -p $dir/{dev,etc,%_lib,var/log}
    cp -a /dev/{null,tty} $dir/dev
    cp /%_lib/{libnss_compat.so.2,libnss_files.so.2} $dir/%_lib
    grep partimag /etc/passwd > $dir/etc/passwd
    grep partimag /etc/group > $dir/etc/group
    install -d -o partimag $dir/data
fi
# now all you have to do is run partimaged -D --chroot /var/lib/partimage
%_post_service partimaged
%_create_ssl_certificate partimage -g partimag

%preun
%_preun_service partimaged

%files -f %{name}.lang
%doc BUGS AUTHORS ABOUT-NLS COPYING ChangeLog
%doc FORMAT README README.partimaged README.omv
%doc THANKS
%{_sbindir}/*
%{_sysconfdir}/sysconfig/partimaged
%{_sysusersdir}/%{name}.conf
%{_initrddir}/partimaged
%attr(0600,partimag,partimag) %config(noreplace) %{_sysconfdir}/partimaged/partimagedusers
%{_mandir}/man1/partimage.1*
%{_mandir}/man5/partimagedusers.5*
%{_mandir}/man8/partimaged.8*
%{_datadir}/doc/partimage/partimage.lsm
