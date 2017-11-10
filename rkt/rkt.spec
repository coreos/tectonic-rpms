%global provider github
%global provider_tld com
%global project0 rkt
%global repo0 rkt
# Definitions to support systemd from source
%global project1 systemd
%global repo1 systemd

%global git0 https://%{provider}.%{provider_tld}/%{project0}/%{repo0}
%global import_path %{provider}.%{provider_tld}/%{project0}/%{repo0}

# These values should match those built into this rkt version
%global coreos_version 1478.0.0
%global coreos_systemd_version 233

# Again... More things to support dyamically building a systemd stage1
# outside of the verison of systemd packaged with Red Hat Enterprise Linux 7
%global git1 https://%{provider}.%{provider_tld}/%{project1}/%{repo1}
%if 0%{?fedora}
%global systemd_version 234
%else
%global systemd_version 222
%endif

# valid values: src coreos host kvm fly
%global stage1_flavors coreos,fly,src

Name:           %{repo0}
Version:        1.29.0
Release:        2%{?dist}
Summary:        A pod-native container engine for Linux

License:        ASL 2.0
URL:            %{git0}

ExclusiveArch:  x86_64 aarch64 %{arm} %{ix86}
# Over time we should validate rkt atop the expanded Go platforms (ppc64le, s390x, etc)
#ExclusiveArch:  %%{go_arches}

Source0:        %{git0}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{git1}/archive/v%{systemd_version}/%{repo1}-%{systemd_version}.tar.gz
Source2:        https://alpha.release.core-os.net/amd64-usr/%{coreos_version}/coreos_production_pxe_image.cpio.gz#/coreos-%{coreos_version}-amd64-usr.cpio.gz
Patch0:         https://github.com/rkt/rkt/commit/ce936a91678b77a2b91440e0198c895519ca8b24.patch#/%{name}-%{version}-multiple-hosts-entry-host.patch

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  bc
BuildRequires:  glibc-static
BuildRequires:  golang >= 1.6
BuildRequires:  gperf
BuildRequires:  gnupg
BuildRequires:  intltool
BuildRequires:  libacl-devel
BuildRequires:  libcap-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  libseccomp-devel
BuildRequires:  libtool
BuildRequires:  libmount-devel
BuildRequires:  systemd-devel >= 219
BuildRequires:  perl-Config-Tiny
BuildRequires:  squashfs-tools

# We are not enabling TPM support so skip trousers
#BuildRequires:  trousers-devel

Requires(pre):  shadow-utils
Requires(post): systemd >= 219
Requires(preun): systemd >= 219
Requires(postun): systemd >= 219

Requires:       iptables

%description
%{summary}.  It is composable, secure, & built
on standards.  Some of rkt's key features and goals include:

* Pod-native: rkt's basic unit of execution is a pod, linking together
resources and user applications in a self-contained environment.

* Security: rkt is developed with a principle of "secure-by-default", and
includes a number of important security features like support for SELinux, TPM
measurement, and running app containers in hardware-isolated VMs.

* Composability: rkt is designed for first-class integration with init systems
(like systemd, upstart) and cluster orchestration tools (like Kubernetes and
Nomad), and supports swappable execution engines.

* Open standards and compatibility: rkt implements the appc specification,
supports the Container Networking Interface specification, and can run Docker
images and OCI images. Broader native support for OCI images and runtimes is
in development.


%prep
%setup -q -n %{repo0}-%{version}
%patch0 -p1

%setup -q -T -D -a 1

%build
./autogen.sh
# ./configure flags: https://github.com/coreos/rkt/blob/master/Documentation/build-configure.md
%configure \
    --with-coreos-local-pxe-image-path=%{SOURCE2} \
    --with-coreos-local-pxe-image-systemd-version=v%{coreos_systemd_version} \
    --with-stage1-flavors=%{stage1_flavors} \
    --with-stage1-flavors-version-override=%{version}-%{project0} \
    --with-stage1-default-location=%{_libexecdir}/%{name}/stage1-coreos.aci \
    --with-stage1-default-images-directory=%{_libexecdir}/%{name} \
    --disable-tpm \
    --with-stage1-systemd-src=%{_builddir}/%{repo0}-%{version}/%{repo1}-%{systemd_version} \
    --with-stage1-systemd-revision=v%{systemd_version} \
    --with-stage1-systemd-version=v%{systemd_version} \
    GIT=true WGET=true  # Bypass this senseless check
%make_build all bash-completion manpages

%install
# install binaries
install -dp %{buildroot}{%{_bindir},%{_libexecdir}/%{name},%{_unitdir},%{_tmpfilesdir}}
install -dp %{buildroot}%{_sharedstatedir}/%{name}

install -dp %{buildroot}%{_sysconfdir}/%{name}/trustedkeys/prefix.d
install -dp %{buildroot}%{_mandir}/man1
install -p -m 644 dist/manpages/*.1 %{buildroot}%{_mandir}/man1

install -p -m 755 build-%{name}-%{version}/target/bin/%{name} %{buildroot}%{_bindir}
install -p -m 644 build-%{name}-%{version}/target/bin/stage1-*.aci %{buildroot}%{_libexecdir}/%{name}

# install bash completion
install -dp %{buildroot}%{_datadir}/bash-completion/completions
install -p -m 644 dist/bash_completion/%{name}.bash %{buildroot}%{_datadir}/bash-completion/completions/%{name}

# install metadata unitfiles
install -p -m 644 dist/init/systemd/%{name}-gc.timer %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-gc.service %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-api.service %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-api-tcp.socket %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-metadata.socket %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/%{name}-metadata.service %{buildroot}%{_unitdir}
install -p -m 644 dist/init/systemd/tmpfiles.d/%{name}.conf %{buildroot}%{_tmpfilesdir}

# setup of data directories
install -dp %{buildroot}%{_sharedstatedir}/%{name}/tmp
install -dp %{buildroot}%{_sharedstatedir}/%{name}/cas/{db,imagelocks,imageManifest,blob,tmp,tree,treestorelocks}
install -dp %{buildroot}%{_sharedstatedir}/%{name}/locks
install -dp %{buildroot}%{_sharedstatedir}/%{name}/pods/{embryo,prepare,prepared,run,garbage,exited-garbage}

touch %{buildroot}%{_sharedstatedir}/%{name}/cas/db/ql.db
touch %{buildroot}%{_sharedstatedir}/%{name}/cas/db/.34a8b4c1ad933745146fdbfef3073706ee571625


%post
%systemd_post %{name}-metadata.service

%postun
%systemd_postun_with_restart %{name}-metadata.service

%pre
getent group %{name} > /dev/null 2>&1 || groupadd -r %{name}
getent group %{name}-admin > /dev/null 2>&1 || groupadd -r %{name}-admin
exit 0

%preun
%systemd_preun %{name}-metadata.service


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc CONTRIBUTING.md DCO README.md Documentation/*
%doc %{_mandir}/man1/rkt.1*
%doc %{_mandir}/man1/rkt_api-service.1*
%doc %{_mandir}/man1/rkt_cat-manifest.1*
%doc %{_mandir}/man1/rkt_completion.1*
%doc %{_mandir}/man1/rkt_config.1*
%doc %{_mandir}/man1/rkt_enter.1*
%doc %{_mandir}/man1/rkt_export.1*
%doc %{_mandir}/man1/rkt_fetch.1*
%doc %{_mandir}/man1/rkt_gc.1*
%doc %{_mandir}/man1/rkt_image.1*
%doc %{_mandir}/man1/rkt_image_cat-manifest.1*
%doc %{_mandir}/man1/rkt_image_export.1*
%doc %{_mandir}/man1/rkt_image_extract.1*
%doc %{_mandir}/man1/rkt_image_gc.1*
%doc %{_mandir}/man1/rkt_image_list.1*
%doc %{_mandir}/man1/rkt_image_render.1*
%doc %{_mandir}/man1/rkt_image_rm.1*
%doc %{_mandir}/man1/rkt_image_verify.1*
%doc %{_mandir}/man1/rkt_list.1*
%doc %{_mandir}/man1/rkt_metadata-service.1*
%doc %{_mandir}/man1/rkt_prepare.1*
%doc %{_mandir}/man1/rkt_rm.1*
%doc %{_mandir}/man1/rkt_run.1*
%doc %{_mandir}/man1/rkt_run-prepared.1*
%doc %{_mandir}/man1/rkt_status.1*
%doc %{_mandir}/man1/rkt_stop.1*
%doc %{_mandir}/man1/rkt_trust.1*
%doc %{_mandir}/man1/rkt_version.1*
%{_bindir}/%{name}
%{_libexecdir}/%{name}/stage1-*.aci
%{_unitdir}/%{name}*
%{_datadir}/bash-completion/completions/%{name}
%{_tmpfilesdir}/%{name}.conf
# I *really* don't like all of these set with the sticky bit, but it is the
# way the upstream develelopers did all of this:
# https://github.com/rkt/rkt/blob/ec37f3cb/dist/scripts/setup-data-dir.sh 
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/tmp
%dir %attr(2770,root,rkt) %{_sharedstatedir}/%{name}/cas
%dir %attr(2770,root,rkt) %{_sharedstatedir}/%{name}/cas/db
%dir %attr(2770,root,rkt) %{_sharedstatedir}/%{name}/cas/imagelocks
%dir %attr(2770,root,rkt) %{_sharedstatedir}/%{name}/cas/imageManifest
%dir %attr(2770,root,rkt) %{_sharedstatedir}/%{name}/cas/blob
%dir %attr(2770,root,rkt) %{_sharedstatedir}/%{name}/cas/tmp
%dir %attr(0700,root,rkt) %{_sharedstatedir}/%{name}/cas/tree
%dir %attr(0700,root,rkt) %{_sharedstatedir}/%{name}/cas/treestorelocks
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/locks
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods/embryo
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods/prepare
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods/prepared
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods/run
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods/exited-garbage
%dir %attr(2750,root,rkt) %{_sharedstatedir}/%{name}/pods/garbage
%dir %config %attr(0775,root,rkt-admin) %{_sysconfdir}/%{name}
%dir %config %attr(0775,root,rkt-admin) %{_sysconfdir}/%{name}/trustedkeys
%dir %config %attr(0775,root,rkt-admin) %{_sysconfdir}/%{name}/trustedkeys/prefix.d

%attr(0660,root,rkt) %{_sharedstatedir}/%{name}/cas/db/ql.db
%attr(0660,root,rkt) %{_sharedstatedir}/%{name}/cas/db/.34a8b4c1ad933745146fdbfef3073706ee571625

%changelog
* Tue Oct 24 2017 David Michael <david.michael@coreos.com> - 1.29.0-2
- Apply a patch for less strict option parsing from upstream.

* Wed Oct 04 2017 David Michael <david.michael@coreos.com> - 1.29.0-1
- Update to 1.29.0.
- Drop the systemd stage1 patch (applied upstream).
- Bump the CoreOS image to 1478.0.0.

* Fri Sep 01 2017 David Michael <david.michael@coreos.com> - 1.28.1-2
- Fetch the systemd stage1 patch from upstream.

* Tue Aug 15 2017 David Michael <david.michael@coreos.com> - 1.28.1-1
- Update to 1.28.1.
- Drop unused clean and check sections.
- Allow the build system to compress man pages.

* Tue Jul 25 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.27.0-1
- "rkt: Bump to 1.27.0"
- "rkt: Build the systemd-from-source stage1"
- "rkt: Keep the CoreOS PXE image in the SRPM"

* Tue Jun 06 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.26.0-2
- "rkt: Added support for rkt_image_verify"

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.26.0-1
- new package built with tito

* Tue Apr 18 2017 Brian 'redbeard' Harrington <redbeard@fedoraproject.org> - 1.25.0-1
- built commit#ec37f3cb (Tagged 1.25.0)

- Packaged rkt but have disabled TPM support at the present time.  In the process
found a number of things to fix upstream including the "usr-from-src" option.

- Initial package largely inspired by the work from Lokesh Mandvekar (lsm5). This RPM
is dedicated to the dilligence of Jon Boulle (@baronboulle) in his stewardship
of rkt (nee rocket), founding of CoreOS GmbH, and dilligent defense of grammar
and style.  Substantial changes were made to properly flag files, include man pages,
and other things important to the Red Hat eco-system.
