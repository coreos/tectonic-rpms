# Tectonic RPMs

This repository hosts the source files to build packages for [Tectonic on Red Hat Enterprise Linux][tectonic-rhel]. Currently, only RHEL 7 on x86_64 is supported.

All packages are built with [Mock][mock]. The file `mock.cfg` can be passed to recent versions of the Mock command like `mock -r mock.cfg ...` to set up the RHEL build environment. Note that it tries to include a non-standard configuration file `/etc/mock/rhel-7-x86_64.cfg`, which should configure repositories of RHEL 7 packages. If that file does not exist, it will fall back to the CentOS 7 repository configuration that is distributed with Mock.

Binary packages built from these sources are published in the [Tectonic repository][tectonic-repo].

For usage instructions, see the [Tectonic RHEL documentation][tectonic-docs].

[mock]: https://github.com/rpm-software-management/mock/wiki
[tectonic-docs]: https://coreos.com/tectonic/docs/latest/install/rhel/installing-workers.html
[tectonic-repo]: https://yum.prod.coreos.systems/repo/tectonic-rhel/7Server/x86_64/repoview/
[tectonic-rhel]: https://coreos.com/tectonic/rhel/
