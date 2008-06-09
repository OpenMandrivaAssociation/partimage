%define	name	partimage 
%define release	%mkrel 4
%define	version	0.6.7

%define jail 0
%{?_with_jail: %{expand: %%global jail 1}}

Summary: 	Partition Image
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
URL: 		http://www.partimage.org/
License: 	GPL
Group: 		Archiving/Backup
Source: 	%{name}-%{version}.tar.bz2
Source1:	partimage.1
Source2:	partimaged.8
Source3:	partimagedusers.5
Source5:	partimaged-init.d
Patch0: 	%{name}-slang.patch
Patch1: 	partimage-0.6.7-chown.patch
Patch2: 	partimage-0.6.5-deb_disable_header_check.patch
Patch3: 	partimage-0.6.7-ssl-certs-policy.patch
Patch4: 	partimage-0.6.7-set-effective-gid.patch
Patch5:		partimage-0.6.7-gcc43.patch
Patch8: 	partimage-0.6.5-save_file_and_rest_file_actions.patch
BuildRequires:	automake1.8
BuildRequires:	bzip2-devel
BuildRequires:	gettext-devel
BuildRequires:	newt-devel
BuildRequires:	openssl
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	rpm-helper >= 0.21
Requires:	openssl > 0.9.6
Requires(post): rpm-helper >= 0.21
Buildroot: 	%{_tmppath}/%{name}-%{version}

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

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%if %{jail}
%patch8 -p1
%endif

for i in %{_datadir}/automake-1.*/mkinstalldirs; do cp -f $i .; done

%build
%if %{jail}
opts="--disable-login --disable-ssl"
%else
opts=
%endif

cp %{_datadir}/gettext/config.rpath .
autoreconf # needed on 2007.0
%configure $opts
%make

%install
rm -rf  $RPM_BUILD_ROOT
%makeinstall

rm -rf %{buildroot}%{_infodir}/*

install -m644 %{SOURCE1} -D %{buildroot}%{_mandir}/man1/partimage.1
install -m644 %{SOURCE2} -D %{buildroot}%{_mandir}/man8/partimaged.8
install -m644 %{SOURCE3} -D %{buildroot}%{_mandir}/man5/partimagedusers.5
%if %{jail}
rm -rf %{buildroot}%{_sysconfdir}/partimaged
install -m755 %{SOURCE5} -D %{buildroot}%{_initrddir}/partimaged
%endif

%find_lang %{name}

%pre
/usr/sbin/groupadd -r -f partimag > /dev/null 2>&1 ||:
/usr/sbin/useradd -g partimag -d /home/partimag -r -s /bin/bash partimag > /dev/null 2>&1 ||:

%post

%if %{jail}
dir=/var/lib/partimage
if [ ! -d $dir ]; then 
    mkdir -p $dir/{dev,etc,%_lib,var/log}
    cp -a /dev/{null,tty} $dir/dev
    cp /%_lib/{libnss_compat.so.2,libnss_files.so.2} $dir/%_lib
    grep partimag /etc/passwd > $dir/etc/passwd
    install -d -o partimag $dir/data
fi
# now all you have to do is run partimaged -D --chroot /var/lib/partimage

%_post_service partimaged

%else
%_create_ssl_certificate partimage -g partimag
%endif

%if %{jail}
%preun
%_preun_service partimaged
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr (-,root,root)
%doc BOOT-ROOT.txt BUGS AUTHORS ABOUT-NLS COPYING ChangeLog
%doc FORMAT FUTURE README README.partimaged 
%doc THANKS TODO
%{_sbindir}/*
%if %{jail}
%{_initrddir}/partimaged
%else
%attr(0600,partimag,partimag) %config(noreplace) %{_sysconfdir}/partimaged/partimagedusers
%endif
%{_mandir}/man1/partimage.1*
%{_mandir}/man5/partimagedusers.5*
%{_mandir}/man8/partimaged.8*


