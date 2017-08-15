%define release_name BlackMaple
%define dist_version 1.6.7
%define bug_version prerelease
# Versions Tagged on Quay.io - https://quay.io/repository/coreos/hyperkube?tab=tags
%define kubelet_version v%{dist_version}_coreos.0
# The Quay public key to trust
%define registry_domain quay.io
%define key_fingerprint bff313cdaa560b16a8987b8f72abf5f6799d33bc

Summary:        A Kubernetes worker configured for Tectonic 
Name:           tectonic-worker
Version:        %{dist_version}
Release:        1%{?dist}
License:        ASL 2.0
Group:          System Environment/Base
URL:            https://coreos.com/tectonic
Source0:        https://raw.githubusercontent.com/coreos/coreos-overlay/master/app-admin/kubelet-wrapper/files/kubelet-wrapper
Source1:        kubelet.path
Source2:        kubelet.service
Source3:        wait-for-dns.service
Source4:        kubelet-wrapper-preflight.sh
Source5:        INSTALL.md
Source6:        %{registry_domain}-%{key_fingerprint}
Patch0:         kubelet-wrapper.patch

BuildArch:      noarch
Requires:       systemd >= 219
Requires:       openssh-server
Requires:       rkt >= 1.25.0
Requires:       docker >= 1.12.0
Conflicts:      kubernetes
Conflicts:      kubernetes-master
Conflicts:      kubernetes-node


%description
Services for the configuration of a Tectonic Kubernetes worker


%prep

%setup -cT
cp -p %{SOURCE0} .
cp -p %{SOURCE1} .
cp -p %{SOURCE2} .
cp -p %{SOURCE3} .
cp -p %{SOURCE4} .
cp -p %{SOURCE5} .

%patch0 -p 1

%{__cat} <<-KUBELET-EOF > kubelet.env
	KUBELET_IMAGE_URL=quay.io/coreos/hyperkube
	KUBELET_IMAGE_TAG=%{kubelet_version}
KUBELET-EOF

%{__cat} <<-KUBESET-EOF > tectonic-worker
	KUBERNETES_DNS_SERVICE_IP=
	CLUSTER_DOMAIN=cluster.local
KUBESET-EOF

%build

%install
install -d %{buildroot}%{_sysconfdir}/{kubernetes,sysconfig}
install -d %{buildroot}%{_pkgdocdir}
install -d %{buildroot}%{_prefix}/lib/{coreos,systemd/system}
install -p -m 755 kubelet-wrapper %{buildroot}%{_prefix}/lib/coreos
install -p -m 755 kubelet-wrapper-preflight.sh %{buildroot}%{_prefix}/lib/coreos
install -p -m 644 kubelet.path %{buildroot}%{_unitdir}
install -p -m 644 kubelet.service %{buildroot}%{_unitdir}
install -p -m 644 wait-for-dns.service %{buildroot}%{_unitdir}
install -p -m 644 kubelet.env %{buildroot}%{_sysconfdir}/kubernetes
install -p -m 644 tectonic-worker %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 644 INSTALL.md %{buildroot}%{_pkgdocdir}

install -d -m 775 %{buildroot}%{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}
install -p -m 664 %{SOURCE6} %{buildroot}%{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}/%{key_fingerprint}


%files
%defattr(-,root,root,-)
%{_prefix}/lib/coreos/kubelet-wrapper
%{_prefix}/lib/coreos/kubelet-wrapper-preflight.sh
%{_unitdir}/kubelet.path
%{_unitdir}/kubelet.service
%{_unitdir}/wait-for-dns.service
%config %{_sysconfdir}/kubernetes/kubelet.env
%ghost %config(missingok) %{_sysconfdir}/kubernetes/kubeconfig
%ghost %config(missingok) %{_sysconfdir}/kubernetes/kube.version
%config(noreplace) %{_sysconfdir}/sysconfig/tectonic-worker
%dir %attr(0775,root,rkt-admin) %{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}
%config %attr(0664,root,rkt-admin) %{_sysconfdir}/rkt/trustedkeys/prefix.d/%{registry_domain}/%{key_fingerprint}
%doc %{_pkgdocdir}/INSTALL.md

%changelog
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
