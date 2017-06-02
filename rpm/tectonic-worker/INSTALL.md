# Tectonic Worker

## About

This RPM installs the Tectonic Worker components as a part of CoreOS Kubernetes.

The Tectonic Worker is runs atop rkt for it's execution plane.  It utilizes the
monolithic Kubernetes image "hyperkube" to bootstrap itself.  The hyperkube
image contacts the CoreOS Kubernetes control plane to configure all components.
These components are dictated by the install and will differ depending on the
installation options.

## Configuring

At runtime, users will need to take two configuration steps:

  - Make relevant changes to `/etc/sysconfig/tectonic-worker`
  - Copy the cluster "Kubeconfig" file to the path `/etc/kubernetes/kubeconfig`

Both the settings for `tectonic-worker` as well as file `kubeconfig` can be
found in the assets created by the [tectonic installer][1].  The file
`kubeconfig` is located in the sub-path `generated/auth/kubeconfig` while the
DNS settings will be located in the file `terraform.tfvars` under the key name
`.tectonic_kube_dns_service_ip`.  As a convenience, users with [JQ][2] installed
can extract this value with the command:

```
$ jq '.tectonic_kube_dns_service_ip' terraform.tfvars
```

The default CNI installation for Tectonic utilizes VXLAN for it's communications
with [flannel][3].  As such, it will need communications between hosts on UDP
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
information consult the [relevant Kubernetes documentation][4].

## SELinux

At the present time a policy allowing the Tectonic Worker has not been completed
and users will have to run SELinux in Permissive mode.  This work may be
completed in the future.

[1]: https://github.com/coreos/tectonic-installer
[2]: https://stedolan.github.io/jq/
[3]: https://github.com/coreos/flannel
[4]: https://coreos.com/kubernetes/docs/latest/kubernetes-networking.html
<!-- vim: ts=2 sw=2 tw=80 expandtab:
-->
