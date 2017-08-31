# Tectonic Worker

## About

This RPM installs the Tectonic Worker components as part of CoreOS Kubernetes.

The Tectonic Worker runs atop rkt for its execution plane.  It utilizes the
monolithic Kubernetes image "hyperkube" to bootstrap itself.  The hyperkube
image contacts the CoreOS Kubernetes control plane to configure all components.
These components are dictated by the install and will differ depending on the
installation options.

## Configuring

At runtime, users will need to take a minimal number of configuration steps:

  - Make relevant changes to `/etc/sysconfig/tectonic-worker`
  - Copy the cluster "Kubeconfig" file to the path `/etc/kubernetes/kubeconfig`
  - Enable and start the `kubelet` service

In some situations users may also need to configure firewalld.

### Copy the `kubeconfig` file from the Tectonic Installer to the host

The [Tectonic Installer][2] generates a `kubeconfig` file which is used by all
Tectonic workers to authenticate to the API server.  As this file is identical
on all hosts, it can be retrieved from an existing worker, a node in the
control plane, or from the assets bundle created by the installer.

To use the `kubeconfig` from the assets bundle, extract the bundle to disk and
then change to the root directory of the extracted bundle.  The file will be
located at the path `generated/auth/kubeconfig`.  Copy the file to the worker
and place it in the path `/etc/kubernetes/kubeconfig`.

### Configure the DNS service address

As a part of the Tectonic system a cluster wide DNS service will be deployed.
To allow the kubelet to discover the location of other pods and services, we
will need to inform the system of the DNS service address.

The DNS service address can be manually extracted from the file
`terraform.tfvars` located in the installer assets directory.  It is located
under the key `tectonic_kube_dns_service_ip`.

As the file `terraform.tfvars` is intended for machine consumption is often
easier to retrieve this value using the utility [jq][3].  If available, this
can be done with the command:

```
$ jq .tectonic_kube_dns_service_ip terraform.tfvars
```

Once this value has been retrieved, it must be defined in the user managed file
`/etc/sysconfig/tectonic-worker` on the host in the field
`KUBERNETES_DNS_SERVICE_IP=`.

### Configure firewalld

The default CNI installation for Tectonic utilizes VXLAN for its communication
with [flannel][4].  As such, it will need to communicate between hosts on UDP
port 4789.  The Kubernetes API will also communicate with hosts on TCP port
10250.  To simplify the configuration of these options either allow all
communications between cluster members, place the relevant Ethernet interfaces
into the "trusted" zone using firewalld, or at a minimum allow `4789/udp` and
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

This process is the same for all systemd hosts.  The service as installed by
the `tectonic-worker` RPM is called `kubelet`.  It can be started with the
command:

```
$ systemctl start kubelet.service
```

It will take a number of minutes for the worker to retrieve the relevant assets
from Quay.io, bootstrap, and join the cluster.  Progress can be monitored with
the command:

```
$ journalctl -fu kubelet.service
```

*NOTE: PolicyKit requires the user to be in a relevant group with access to the
journal.  By default Red Hat provides the groups `adm` and `systemd-journal`
for this purpose.  Alternatively the command can be run as the root user.*

To ensure the service starts on each boot run the command:

```
$ systemctl enable kubelet.service
```

### SELinux

At the present time a policy allowing the Tectonic Worker has not been
completed, and users must run SELinux in Permissive mode.  The ability to run
in Enforcing mode may be completed in the future.

## Troubleshooting

[1]: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/index.html
[2]: https://github.com/coreos/tectonic-installer
[3]: https://stedolan.github.io/jq/
[4]: https://github.com/coreos/flannel
[5]: https://coreos.com/kubernetes/docs/latest/kubernetes-networking.html
<!-- vim: ts=2 sw=2 tw=80 expandtab:
-->
