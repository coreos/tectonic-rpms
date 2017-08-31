%define dist_version 1.7.1
# Versions Tagged on Quay.io - https://quay.io/repository/coreos/hyperkube?tab=tags
%define kubelet_version v%{dist_version}_coreos.0
# The Quay public key to trust
%define registry_domain quay.io
%define key_fingerprint bff313cdaa560b16a8987b8f72abf5f6799d33bc

Name:           tectonic-worker
Version:        %{dist_version}
Release:        1%{?dist}
Summary:        A Kubernetes worker configured for Tectonic

Group:          System Environment/Daemons
License:        ASL 2.0
URL:            https://coreos.com/tectonic

Source0:        https://raw.githubusercontent.com/coreos/coreos-overlay/77d54112ae016b3d54f9ed4ade9db07a46db02f7/app-admin/kubelet-wrapper/files/kubelet-wrapper#/coreos-1506.0.0-kubelet-wrapper
Source1:        kubelet.path
Source2:        kubelet.service
Source3:        wait-for-dns.service
Source4:        kubelet-wrapper-preflight.sh
Source5:        INSTALL.md
Source6:        %{registry_domain}-%{key_fingerprint}
Source7:        %{name}-%{version}-LICENSE
Patch0:         kubelet-wrapper.patch

BuildArch:      noarch
Requires:       systemd >= 219
Requires:       openssh-server
Requires:       rkt >= 1.25.0
Requires:       docker >= 1.12.0
Conflicts:      kubernetes
Conflicts:      kubernetes-master
Conflicts:      kubernetes-node

%systemd_requires

%description
Services for the configuration of a Tectonic Kubernetes worker


%prep
%setup -cT
cp -p %{SOURCE0} kubelet-wrapper
cp -p %{SOURCE1} .
cp -p %{SOURCE2} .
cp -p %{SOURCE3} .
cp -p %{SOURCE4} .
cp -p %{SOURCE5} .
cp -p %{SOURCE6} quay-key
cp -p %{SOURCE7} LICENSE

%patch0 -p1

%{__cat} <<- 'KUBELET-EOF' > kubelet.env
	KUBELET_IMAGE_URL=quay.io/coreos/hyperkube
	KUBELET_IMAGE_TAG=%{kubelet_version}
KUBELET-EOF

%{__cat} <<- 'KUBESET-EOF' > tectonic-worker
	KUBERNETES_DNS_SERVICE_IP=
	CLUSTER_DOMAIN=cluster.local
KUBESET-EOF

%build

%install
install -dm 0755 %{buildroot}%{_prefix}/lib/coreos
install -pm 0755 kubelet-wrapper \
    %{buildroot}%{_prefix}/lib/coreos/kubelet-wrapper
install -pm 0755 kubelet-wrapper-preflight.sh \
    %{buildroot}%{_prefix}/lib/coreos/kubelet-wrapper-preflight.sh

for unit in kubelet.path kubelet.service wait-for-dns.service
do install -Dpm 0644 $unit %{buildroot}%{_unitdir}/$unit
done

install -dm 0755 %{buildroot}%{_sysconfdir}/kubernetes
install -pm 0644 kubelet.env %{buildroot}%{_sysconfdir}/kubernetes/kubelet.env

install -Dpm 0644 tectonic-worker \
    %{buildroot}%{_sysconfdir}/sysconfig/tectonic-worker

install -dm 0775 %{buildroot}%{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}
install -pm 0664 quay-key \
    %{buildroot}%{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}/%{key_fingerprint}


%post
%systemd_post kubelet.path kubelet.service wait-for-dns.service

%postun
# Don't restart automatically; let administrators schedule their own downtime.
%systemd_postun

%preun
%systemd_preun kubelet.path kubelet.service wait-for-dns.service


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%{_prefix}/lib/coreos
%{_unitdir}/kubelet.path
%{_unitdir}/kubelet.service
%{_unitdir}/wait-for-dns.service
%dir %{_sysconfdir}/kubernetes
%config %{_sysconfdir}/kubernetes/kubelet.env
%ghost %config(missingok) %{_sysconfdir}/kubernetes/kubeconfig
%ghost %config(missingok) %{_sysconfdir}/kubernetes/kube.version
%config(noreplace) %{_sysconfdir}/sysconfig/tectonic-worker
%dir %attr(0775,root,rkt-admin) %{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}
%config %attr(0664,root,rkt-admin) %{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}/%{key_fingerprint}
%doc INSTALL.md

%changelog
* Tue Aug 15 2017 David Michael <david.michael@coreos.com> - 1.7.1-1
- Update to 1.7.1.
- Trust the Quay key by default in this package instead of tectonic-release.
- Update the kubelet-wrapper script, and version its source file.

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.4-3
- "Adding INSTALL.md and conforming to /etc/sysconfig"

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.4-2
- bug: Don't replace kubesettings-local.env on upgrade
  (brian.harrington@coreos.com)

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com>
- bug: Don't replace kubesettings-local.env on upgrade
  (brian.harrington@coreos.com)

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.4-1
- release: Bumping for Kubernetes version 1.6.4 (brian.harrington@coreos.com)

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.2-3
- release: Catching up on 1.6.2 release changes 
- Added a pre-flight check to make things as easy as possible for end users.
- bug: Preflight used stderr incorrectly 
- typo: Invalid paths in kubelet.service 
- Remove TOFU from Quay.io 
- typo: misspelling of kubelet-wrapper-preflight.sh 
- rhel/preflight: Adding systemd preflight checks 
- init/tectonic-worker: Checkin of tectonic-worker 

* Tue May 30 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.6.2-2
- Pulled in new kubelet wrapper which vendors volume names with coreos-

* Fri May 19 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.6.2-1
- Packaged Tectonic release 1.6.2-1

* Thu Apr 27 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.5.7-1
- Packaged Tectonic release 1.5.7-1
- Includes license definition, repo file, GPG, and an initial mirrorlist.
