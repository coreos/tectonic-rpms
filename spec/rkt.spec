%global provider github
%global provider_tld com
%global project0 rkt
%global repo0 rkt
%global project1 systemd
%global repo1 systemd

%global git0 https://%{provider}.%{provider_tld}/%{project0}/%{repo0}
%global git1 https://%{provider}.%{provider_tld}/%{project1}/%{repo1}
%global import_path %{provider}.%{provider_tld}/%{project0}/%{repo0}
%global systemd_version 231

# valid values: coreos usr-from-src usr-from-host kvm
%global stage1_flavors coreos,fly

Name: %{repo0}
Version: 1.25.0
Release: 1%{?dist}
Summary: rkt is a pod-native container engine for Linux

License: ASL 2.0
URL: %{git0}
ExclusiveArch: x86_64 aarch64 %{arm} %{ix86}
# Over time we should validate rkt atop the expanded Go platforms (ppc64le, s390x, etc)
#ExclusiveArch: %{go_arches}
Source0: %{git0}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1: %{git1}/archive/v%{systemd_version}/%{repo1}-%{systemd_version}.tar.gz
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bc
BuildRequires: glibc-static
BuildRequires: golang >= 1.6
BuildRequires: gperf
BuildRequires: gnupg
BuildRequires: intltool
BuildRequires: libacl-devel
BuildRequires: libcap-devel
BuildRequires: libgcrypt-devel
BuildRequires: libtool
BuildRequires: libmount-devel
BuildRequires: systemd-devel >= 219
BuildRequires: perl-Config-Tiny
BuildRequires: squashfs-tools
BuildRequires: scl-utils-build
BuildRequires: wget
BuildRequires: git19
# Unfortunately, boolean dependencies didn't make it into RPM 4.11
#BuildRequires: (git >= 1.8.5 or git19 or rh-git29)

# We are not enabling TPM support so skip trousers
# BuildRequires: trousers-devel

Requires(pre): shadow-utils
Requires(post): systemd >= 219
Requires(preun): systemd >= 219
Requires(postun): systemd >= 219

Requires: iptables
Requires: systemd-container

%description
%{summary}.  It is composable, secure, & built
on standards.  Some of rkt's key features and goals include:

* Pod-native: rkt's basic unit of execution is a pod, linking together resources
and user applications in a self-contained environment.

* Security: rkt is developed with a principle of "secure-by-default", and includes
a number of important security features like support for SELinux, TPM
measurement, and running app containers in hardware-isolated VMs.

* Composability: rkt is designed for first-class integration with init systems
(like systemd, upstart) and cluster orchestration tools (like Kubernetes and
Nomad), and supports swappable execution engines.

* Open standards and compatibility: rkt implements the appc specification,
supports the Container Networking Interface specification, and can run Docker
images and OCI images. Broader native support for OCI images and runtimes is in
development.

%prep
ls -l 
%setup -q -n  %{repo0}-%{version}

# In the future hopefully we can use this to use locally tar'd systemd sources
#%setup -q -T -D -a 1

%build
# This is not as elegant as I'd like, but it gets the job done of allowing a
# user to install git via software collections or use a modern version of the
# package - rb
if [ -f /opt/rh/git19/enable ]; then
	if [ -f /opt/rh/rh-git29/enable ] ; then
		source /opt/rh/rh-git29/enable
	else
		source /opt/rh/git19/enable
	fi
fi

if [ -f /opt/rh/rh-git29/enable ] ; then
	source /opt/rh/rh-git29/enable
fi
	
./autogen.sh
# ./configure flags: https://github.com/coreos/rkt/blob/master/Documentation/build-configure.md
./configure --with-stage1-flavors=%{stage1_flavors} \
            --with-stage1-flavors-version-override=%{version}-%{project0} \
            --with-stage1-default-location=%{_libexecdir}/%{name}/stage1-coreos.aci \
            --with-stage1-default-images-directory=%{_libexecdir}/%{name} \
            --enable-tpm=no 

            #--with-stage1-systemd-src=%{_builddir}/%{repo1}-%{systemd_version} \
            #--with-stage1-systemd-revision=v%{systemd_version} \
            #--with-stage1-systemd-version=v%{systemd_version} \
GOPATH=%{gopath}:$(pwd)/Godeps/_workspace make all bash-completion manpages
gzip dist/manpages/*.1

%install
# install binaries
install -dp %{buildroot}{%{_bindir},%{_libexecdir}/%{name},%{_unitdir}}
install -dp %{buildroot}%{_sharedstatedir}/%{name}

install -dp %{buildroot}%{_sysconfdir}/%{name}/trustedkeys/prefix.d
install -dp %{buildroot}%{_mandir}/man1
install -p -m 644 dist/manpages/*.1.gz %{buildroot}%{_mandir}/man1

install -p -m 755 build-%{name}-%{version}/target/bin/%{name} %{buildroot}%{_bindir}
install -p -m 644 build-%{name}-%{version}/target/bin/stage1-*.aci %{buildroot}%{_libexecdir}/%{name}

# install bash completion
install -dp %{buildroot}%{_datadir}/bash-completion/completions
install -p -m 644 dist/bash_completion/%{name}.bash %{buildroot}%{_datadir}/bash-completion/completions/%{name}

# install metadata unitfiles
install -p -m 644 dist/init/systemd/%{name}-gc.timer %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-gc.service %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-metadata.socket %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-metadata.service %{buildroot}%{_unitdir}

# setup of data directories
install -dp %{buildroot}%{_sharedstatedir}/%{name}/tmp
install -dp %{buildroot}%{_sharedstatedir}/%{name}/cas/{db,imagelocks,imageManifest,blob,tmp,tree,treestorelocks}
install -dp %{buildroot}%{_sharedstatedir}/%{name}/locks
install -dp %{buildroot}%{_sharedstatedir}/%{name}/pods/{embryo,prepare,prepared,run,garbage,exited-garbage}

touch %{buildroot}%{_sharedstatedir}/%{name}/cas/db/ql.db
touch %{buildroot}%{_sharedstatedir}/%{name}/cas/db/.34a8b4c1ad933745146fdbfef3073706ee571625


%check

%clean 
rm -rf %{buildroot}

%pre
getent group %{name} > /dev/null 2>&1 || groupadd -r %{name}
getent group %{name}-admin > /dev/null 2>&1 || groupadd -r %{name}-admin
exit 0

%post
%systemd_post %{name}-metadata.service

%preun
%systemd_preun %{name}-metadata.service

%postun
%systemd_postun_with_restart %{name}-metadata.service

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc CONTRIBUTING.md DCO README.md Documentation/*
%doc %{_mandir}/man1/rkt.1.gz
%doc %{_mandir}/man1/rkt_api-service.1.gz
%doc %{_mandir}/man1/rkt_cat-manifest.1.gz
%doc %{_mandir}/man1/rkt_config.1.gz
%doc %{_mandir}/man1/rkt_enter.1.gz
%doc %{_mandir}/man1/rkt_export.1.gz
%doc %{_mandir}/man1/rkt_fetch.1.gz
%doc %{_mandir}/man1/rkt_gc.1.gz
%doc %{_mandir}/man1/rkt_image.1.gz
%doc %{_mandir}/man1/rkt_image_cat-manifest.1.gz
%doc %{_mandir}/man1/rkt_image_export.1.gz
%doc %{_mandir}/man1/rkt_image_extract.1.gz
%doc %{_mandir}/man1/rkt_image_gc.1.gz
%doc %{_mandir}/man1/rkt_image_list.1.gz
%doc %{_mandir}/man1/rkt_image_render.1.gz
%doc %{_mandir}/man1/rkt_image_rm.1.gz
%doc %{_mandir}/man1/rkt_list.1.gz
%doc %{_mandir}/man1/rkt_metadata-service.1.gz
%doc %{_mandir}/man1/rkt_prepare.1.gz
%doc %{_mandir}/man1/rkt_rm.1.gz
%doc %{_mandir}/man1/rkt_run.1.gz
%doc %{_mandir}/man1/rkt_run-prepared.1.gz
%doc %{_mandir}/man1/rkt_status.1.gz
%doc %{_mandir}/man1/rkt_stop.1.gz
%doc %{_mandir}/man1/rkt_trust.1.gz
%doc %{_mandir}/man1/rkt_version.1.gz
%{_bindir}/%{name}
%{_libexecdir}/%{name}/stage1-*.aci
%{_unitdir}/%{name}*
%{_datadir}/bash-completion/completions/%{name}
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/tmp
%dir %attr(2770, root, rkt) %{_sharedstatedir}/%{name}/cas
%dir %attr(2770, root, rkt) %{_sharedstatedir}/%{name}/cas/db
%dir %attr(2770, root, rkt) %{_sharedstatedir}/%{name}/cas/imagelocks
%dir %attr(2770, root, rkt) %{_sharedstatedir}/%{name}/cas/imageManifest
%dir %attr(2770, root, rkt) %{_sharedstatedir}/%{name}/cas/blob
%dir %attr(2770, root, rkt) %{_sharedstatedir}/%{name}/cas/tmp
%dir %attr(2700, root, rkt) %{_sharedstatedir}/%{name}/cas/tree
%dir %attr(2700, root, rkt) %{_sharedstatedir}/%{name}/cas/treestorelocks
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/locks
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods/embryo
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods/prepare
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods/prepared
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods/run
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods/exited-garbage
%dir %attr(2750, root, rkt) %{_sharedstatedir}/%{name}/pods/garbage
%dir %config %attr(2775, root, rkt-admin) %{_sysconfdir}/%{name}
%dir %config %attr(2775, root, rkt-admin) %{_sysconfdir}/%{name}/trustedkeys
%dir %config %attr(2775, root, rkt-admin) %{_sysconfdir}/%{name}/trustedkeys/prefix.d

%attr(0660, root, rkt) %{_sharedstatedir}/%{name}/cas/db/ql.db
%attr(0660, root, rkt) %{_sharedstatedir}/%{name}/cas/db/.34a8b4c1ad933745146fdbfef3073706ee571625

%changelog
* Tue Apr 18 2017 Brian 'redbeard' Harrington <redbeard@fedoraproject.org> - 1.25.0-1
- built commit#ec37f3cb (Tagged 1.25.0)

- Packaged rkt but have disabled TPM support at the present time.  In the process
found a number of things to fix upstream including the "usr-from-src" option.

- Initial package largely inspired by the work from Lokesh Mandvekar (lsm5). This RPM
is dedicated to the dilligence of Jon Boulle (@baronboulle) in his stewardship
of rkt (nee rocket), founding of CoreOS GmbH, and dilligent defense of grammar
and style.  Substantial changes were made to properly flag files, include man pages,
and other things important to the Red Hat eco-system.
