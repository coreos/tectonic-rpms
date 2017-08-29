%define release_name BlackMaple

Name:           tectonic-release
Version:        7
Release:        1%{?dist}
Summary:        Tectonic release files and repository configuration

Group:          System Environment/Base
License:        ASL 2.0
URL:            https://coreos.com/tectonic

Source0:        %{name}-%{version}-RPM-GPG-KEY-Tectonic
Source1:        %{name}-%{version}-tectonic.repo
Source2:        %{name}-%{version}-LICENSE

BuildArch:      noarch
Requires:       systemd >= 219

%description
Tectonic release files including the /etc/tectonic-version file, signing keys
and RPM repository files.

%prep
%setup -cT

for file in %{sources}
do cp -p "${file}" "${file##*/%{name}-%{version}-}"
done

echo "Tectonic release %{version} (%{release_name})" > tectonic-release
touch --reference=tectonic.repo tectonic-release  # timestamp reproducibility

%{_fixperms} .

%build

%install
install -Dpm 0644 tectonic-release \
    %{buildroot}%{_sysconfdir}/tectonic-release
ln -fns tectonic-release %{buildroot}%{_sysconfdir}/kubernetes-release

install -Dpm 0644 tectonic.repo \
    %{buildroot}%{_sysconfdir}/yum.repos.d/tectonic.repo

install -Dpm 0644 RPM-GPG-KEY-Tectonic \
    %{buildroot}%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-Tectonic


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config(noreplace) %{_sysconfdir}/yum.repos.d/tectonic.repo
%config %{_sysconfdir}/tectonic-release
%{_sysconfdir}/kubernetes-release
%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-Tectonic

%changelog
* Tue Aug 15 2017 David Michael <david.michael@coreos.com> - 7-1
- Bump the version to avoid hinting at a relation to the Tectonic version.
- Define the GPG key path in the repository configuration.
- Drop the Quay key from this package.
- Don't override user modifications to the repository configuration.

* Wed Jul 12 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.2-5
- "bug/yum: dist macro used in place of $releasever"

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.2-4
- Yum repo URL Update (brian.harrington@coreos.com)
- Automatic commit of package [tectonic-release] release [1.6.2-3].
  (brian.harrington@coreos.com)
- release: Catching up on 1.6.2 release changes (redbeard@dead-city.org)

* Fri Jun 02 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> 1.6.2-3
- fix: tectonic-release does not depend on rkt
- fix: Incorrect version in specfile

* Thu May 25 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.6.2-1
- Packaged Tectonic release 1.6.2-1

* Thu Apr 27 2017 Brian 'redbeard' Harrington <brian.harrington@coreos.com> - 1.5.7-1
- Packaged Tectonic release 1.5.7-1
- Includes license definition, repo file, GPG, and an initial mirrorlist.
