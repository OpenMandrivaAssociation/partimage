%bcond_without	uclibc

Summary: 	Partition Image
Name: 		partimage
Version: 	0.6.9
Release: 	3
URL: 		http://www.partimage.org/
License: 	GPL
Group: 		Archiving/Backup
Source0: 	%{name}-%{version}.tar.bz2
Source1:	partimage.1
Source2:	partimaged.8
Source3:	partimagedusers.5
Source4:	partimaged-sysconfig
Source5:	partimaged-init.d
Patch3: 	partimage-0.6.7-ssl-certs-policy.patch
Patch13:	partimage-0.6.7-splash.patch
Patch14:	partimage-0.6.9-dereference-gzFile-pointer.patch
Patch15:	partimage-0.6.9-lzma.patch
Patch16:	partimage-0.6.9-statically-link-partimage-against-libslang.patch
BuildRequires:	automake1.8
BuildRequires:	bzip2-devel
BuildRequires:	gettext-devel
BuildRequires:	liblzma-devel
BuildRequires:	newt-devel
BuildRequires:	slang-static-devel
BuildRequires:	openssl
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	rpm-helper >= 0.21
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-16
BuildRequires:	uClibc++-devel
%endif
Requires:	openssl > 0.9.6
Requires(post): rpm-helper >= 0.21

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

%package -n	uclibc-%{name}
Summary:	Partition Image (uClibc build)
Group: 		Archiving/Backup

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

%prep
%setup -q
%patch3 -p1
%patch13 -p1 -b .gzfile_deref~
%patch14 -p1 -b .splash~
%patch15 -p1 -b .lzma~
%patch16 -p1 -b .slang_static~

autoreconf -fi

%build
CONFIGURE_TOP=$PWD

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
		--disable-ssl \
		--disable-pam
%make
popd
%endif

mkdir -p glibc
pushd glibc
%configure2_5x
%make
popd

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
rm -r %{buildroot}%{uclibc_root}%{_datadir}
%endif

%makeinstall_std -C glibc

install -m644 %{SOURCE1} -D %{buildroot}%{_mandir}/man1/partimage.1
install -m644 %{SOURCE2} -D %{buildroot}%{_mandir}/man8/partimaged.8
install -m644 %{SOURCE3} -D %{buildroot}%{_mandir}/man5/partimagedusers.5
install -m644 %{SOURCE4} -D %{buildroot}%{_sysconfdir}/sysconfig/partimaged
install -m755 %{SOURCE5} -D %{buildroot}%{_initrddir}/partimaged

cat > README.mdv <<EOF
Mandriva RPM specific notes

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

%pre
/usr/sbin/groupadd -r -f partimag > /dev/null 2>&1 ||:
/usr/sbin/useradd -g partimag -d /home/partimag -r -s /bin/bash partimag > /dev/null 2>&1 ||:

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
%doc FORMAT README README.partimaged README.mdv
%doc THANKS
%{_sbindir}/*
%{_sysconfdir}/sysconfig/partimaged
%{_initrddir}/partimaged
%attr(0600,partimag,partimag) %config(noreplace) %{_sysconfdir}/partimaged/partimagedusers
%{_mandir}/man1/partimage.1*
%{_mandir}/man5/partimagedusers.5*
%{_mandir}/man8/partimaged.8*

%if %{with uclibc}
%files -n uclibc-%{name}
%{uclibc_root}%{_sbindir}/partimage
%{uclibc_root}%{_sbindir}/partimaged
%endif
