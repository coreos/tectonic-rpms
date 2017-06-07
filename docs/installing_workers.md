# Installing Tectonic workers on Red Hat Enterprise Linux

## About

Installing the Tectonic worker components atop Red Hat Enterprise Linux affords
additional benefits in juxtaposition to CoreOS Container Linux.  The flexibility
of adding drivers to Red Hat is trivial thus allowing for more specialized
workloads and hardware.

## Architecture

### Deployment Ideology

Deployment of Tectonic workers atop Red Hat Enterprise Linux is modeled after
the traditional methods of installing software on RHEL and *not* that of CoreOS
Container Linux.  As such it is expected that users will be familiar with the
Red Hat packagement system, RPM as well as it's common transport mechanism
YUM/DNF.

As this deployment model is Red Hat focused, it is expected that the technical
steps are performed in whatever manner the user executes today for the rest of
their Red Hat infrastructure.  This can be manual steps (as executed here),
orchestrated through Kickstart/Anaconda, or using some orchestration/configuration
management system like Ansible.

### Execution Ideology

While the _installation_ of the Tectonic worker components is designed to fit
within a traditional Red Hat focused environment, the _execution_ of the
binaries are intended to mirror that of CoreOS Container Linux.  As such a
utility called "`kubelet-wrapper`" will spin up a copy of "`hyperkube`" inside
`rkt`.  This containerized Kubernetes binary reads it's configuration from a
combination of configuration files managed by both the administrator and by
CoreOS.  CoreOS managed files are deployed either in RPM files or via Tectonic
operators.  When files are deployed via RPM local overrides are possible (but
discouraged).  For files deployed via the Tectonic operators, the entire
lifecycle is expected to be mananged by the Tectonic platform.

## Technical Steps

The deployment of a Tectonic worker atop Red Hat Enterprise Linux can be
simplified to a few steps outlined below.

### Deploy Red Hat Enterprise Linux

The deployment of RHEL can be completed in whatever mechanism the user is most
comfortable with ranging from an optical disk installation through a netbooted
installation and all the way to an image based deployment (as is normally the
case with VMWare and OpenStack).  Consult the documentation for your preferred
installation method for assistance - [Red Hat Enterprise Linux Install
Documentation][1]


### Enable "extras" repo
After the basic installation of a host is complete, users will need to ensure
that the additional Red Hat Enterprise Linux repository "extras" is included.
For users of `subscription-manager` this can completed with the command:

```
$ subscription-manager repos --enable=rhel-7-server-extras-rpms
```

For users not leveraging subscription-manager, ensure that the correct URL for
the mirror of extras that is to be used is placed in the corresponding file in
`/etc/yum.repos.d` and set to enabled.

### Install the `tectonic-release` RPM

The `tectonic-release` RPM includes the repo definition for the Tectonic
software as well as relevant signing keys.  The GPG signing key fingerprint for
CoreOS shipped RPMs is:

`3681 363D B1AA 55E0 33A2  7699 CF86 6CFE 1643 1E6A`

Download the RPM from the CoreOS yum repository:

```
$ curl -LJO http://yum.prod.coreos.systems/repo/tectonic-rhel/el7/x86_64/Packages/tectonic-release-1.6.2-4.el7.noarch.rpm
```

Verify the signature:

```
$ rpm -qip tectonic-release-1.6.2-4.el7.noarch.rpm
Name        : tectonic-release
Version     : 1.6.2
Release     : 4.el7
Architecture: noarch
Install Date: (not installed)
Group       : System Environment/Base
Size        : 22899
License     : ASL 2.0
Signature   : RSA/SHA256, Fri 02 Jun 2017 01:01:53 PM PDT, Key ID cf866cfe16431e6a
Source RPM  : tectonic-release-1.6.2-4.el7.src.rpm
Build Date  : Fri 02 Jun 2017 01:01:04 PM PDT
Build Host  : buildhost.tectonic.coreos.systems
Relocations : (not relocatable)
URL         : https://coreos.com/tectonic
Summary     : Tectonic release files and repository configuration
Description :
Tectonic release files including the /etc/tectonic-version file, signing keys
and RPM repository files.
```

It will be noted that the signature on the RPM matches the last 16 characters of
the fingerprint ID above.

After this is completed it can be installed with:

```
$ yum localinstall tectonic-release-1.6.2-4.el7.noarch.rpm
```

### Install the `tectonic-worker` RPM

After the `tectonic-release` RPM is installed the installation of the
`tectonic-worker` RPM is completed with the command:

```
$ yum install tectonic-worker
```

This will download the relevant dependencies and then prompt to validate the
GPG key installed by the `tectonic-release` RPM.

### Copy the `kubeconfig` file from the Tectonic Installer to the host

The [Tectonic installer][2] generates a `kubeconfig` file which is used by all
Tectonic workers to authenticate to the API server.  As this file is identical
on all hosts, it can be retrieved from an existing worker, a node in the
control plane, or from the assets bundle created by the installer.

To use the `kubeconfig` from the assets bundle, extract the bundle to disk and
then change to the root directory of the extracted bundle.  The file will be
located at the path `generated/auth/kubeconfig`.  Copy the file to the worker
and place it in the path `/etc/kubernetes/kubeconfig`.

### Configure the DNS service address

As a part of the Tectonic system a cluster wide DNS service will be deployed.
To allow the kubelet to discover the location of other pods and services we will
need to inform the system of the DNS service address.

The DNS service address can be manually extracted from the file
`terraform.tfvars` located in the installer assets directory.  It is located
under the key `tectonic_kube_dns_service_ip`.

As the file `terraform.tfvars` is intended for machine consumption is often
easier to retrieve this value using the utility [jq][3].  If available, this
can be done with the command:

```
$ jq .tectonic_kube_dns_service_ip terraform.tfvars
```

Once this value has been retrieved it will be placed in the user managed file
`/etc/sysconfig/tectonic-worker` on the host in the field `KUBERNETES_DNS_SERVICE_IP=`.

### Configure Firewalld

The default CNI installation for Tectonic utilizes VXLAN for it's communications
with [flannel][4].  As such, it will need communications between hosts on UDP
port 4789.  The Kubernetes API will also communicate with hosts on TCP port
10250.  To simplify the configuration of these options either allow all
communications between cluster members, place the relevant ethernet interfaces
into the "trusted" zone using FirewallD, or at a minimum allow `4789/udp` and
`10250/tcp`.  These last steps can be completed with the commands:

```
$ firewall-cmd --add-port 10250/tcp
$ firewall-cmd --add-port 10250/tcp --permanent
$ firewall-cmd --add-port 4789/udp
$ firewall-cmd --add-port 4789/udp --permanent
```

Note: These settings may not be all inclusive and will not represent relative
node ports or other communications which may need to be performed.  For more
information consult the [relevant Kubernetes documentation][5].

### Enable and start the service

This process is the same as with all systemd hosts.  The service as installed by
the `tectonic-worker` RPM is called `kubelet`.  It can be started with the
command:

```
$ systemctl start kubelet.service
```

It will take a number of minutes for the worker to retrieve the relevant assets
from Quay.io, bootstrap, and join the cluster.  Progress can be monitored with
the command:

```
$ journalctl -u kubelet.service
```

*NOTE: PolicyKit requires the user to be in a relevant group with access to the
journal.  By default Red Hat provides the groups `adm` and `systemd-journal` for
this purpose.  Alternatively the command can be run as the root user*

To ensure the service starts on each boot run the command:

```
$ systemctl enable kubelet.service
```

### SELinux

At the present time a policy allowing the Tectonic Worker has not been completed
and users must run SELinux in Permissive mode.  The ability to run in Enforcing
mode may be completed in the future.


## Troubleshooting

[1]: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/index.html
[2]: https://github.com/coreos/tectonic-installer
[3]: https://stedolan.github.io/jq/
[4]: https://github.com/coreos/flannel
[5]: https://coreos.com/kubernetes/docs/latest/kubernetes-networking.html
<!-- vim: ts=2 sw=2 tw=80 expandtab:
-->
