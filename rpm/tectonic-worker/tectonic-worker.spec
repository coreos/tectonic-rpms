%define release_name BlackMaple
%define dist_version 1.6.2
%define bug_version prerelease
# Versions Tagged on Quay.io - https://quay.io/repository/coreos/hyperkube?tab=tags
%define kubelet_version v1.6.2_coreos.0

Summary:        A Kubernetes worker configured for Tectonic 
Name:           tectonic-worker
Version:        %{dist_version}
Release:        3%{?dist}
License:        ASL 2.0
Group:          System Environment/Base
URL:            https://coreos.com/tectonic
Source0:        https://raw.githubusercontent.com/coreos/coreos-overlay/master/app-admin/kubelet-wrapper/files/kubelet-wrapper
Source1:     	kubelet-env.service
Source2:     	kubelet.path
Source3:     	kubelet.service
Source4:     	wait-for-dns.service
Source5:     	kubelet-wrapper-preflight.sh
Patch0:		kubelet-wrapper.patch

Provides:       kubernetes-release
Provides:       kubernetes-release(%{version})

BuildArch:      noarch
Requires:	systemd
Requires:	openssh-server
Requires:	rkt
Requires:	docker
Conflicts:	kubernetes


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

%{__cat} <<-KUBESET-EOF > kubesettings-local.env
	KUBERNETES_DNS_SERVICE_IP=
	CLUSTER_DOMAIN=cluster.local
KUBESET-EOF

%build

%install
install -d %{buildroot}%{_sysconfdir}/kubernetes
install -d %{buildroot}%{_prefix}/lib/{coreos,systemd/system}
install -p -m 755 kubelet-wrapper %{buildroot}%{_prefix}/lib/coreos
install -p -m 755 kubelet-wrapper-preflight.sh %{buildroot}%{_prefix}/lib/coreos
install -p -m 644 kubelet-env.service %{buildroot}%{_unitdir}
install -p -m 644 kubelet.path %{buildroot}%{_unitdir}
install -p -m 644 kubelet.service %{buildroot}%{_unitdir}
install -p -m 644 wait-for-dns.service %{buildroot}%{_unitdir}
install -p -m 644 kubelet.env %{buildroot}%{_sysconfdir}/kubernetes
install -p -m 644 kubesettings-local.env %{buildroot}%{_sysconfdir}/kubernetes


%files
%defattr(-,root,root,-)

%{_prefix}/lib/coreos/kubelet-wrapper
%{_prefix}/lib/coreos/kubelet-wrapper-preflight.sh
%{_unitdir}/kubelet-env.service
%{_unitdir}/kubelet.path
%{_unitdir}/kubelet.service
%{_unitdir}/wait-for-dns.service
%{_sysconfdir}/kubernetes/kubelet.env
%{_sysconfdir}/kubernetes/kubesettings-local.env

%changelog
* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.2-3
- release: Catching up on 1.6.2 release changes 
- bug: Preflight used stderr incorrectly 
- typo: Invalid paths in kubelet.service 
- Remove TOFU from Quay.io 
- typo: misspelling of kubelet-wrapper-preflight.sh 
- rhel/preflight: Adding systemd preflight checks 
- init/tectonic-worker: Checkin of tectonic-worker 

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com>
- Automatic commit of package [tectonic-worker] release [1.6.2-3]
- release: Catching up on 1.6.2 release changes 
- bug: Preflight used stderr incorrectly 
- typo: Invalid paths in kubelet.service 
- Remove TOFU from Quay.io 
- typo: misspelling of kubelet-wrapper-preflight.sh 
- rhel/preflight: Adding systemd preflight checks 
- init/tectonic-worker: Checkin of tectonic-worker 

* Thu Jun 01 2017 Brian 'Redbeard' Harrington 1.6.2-3
- new package built with tito

- Added a pre-flight check to make things as easy as possible for end users.
* Tue May 30 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.6.2-2
- Pulled in new kubelet wrapper which vendors volume names with coreos-

* Fri May 19 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.6.2-1
- Packaged Tectonic release 1.6.2-1

* Thu Apr 27 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.5.7-1
- Packaged Tectonic release 1.5.7-1
- Includes license definition, repo file, GPG, and an initial mirrorlist.
