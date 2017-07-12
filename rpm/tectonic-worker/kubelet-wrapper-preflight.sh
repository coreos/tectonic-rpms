#!/bin/bash
set +o pipefail
set +o nounset
set +o errexit

KUBE_SETTINGS_LOCAL="/etc/sysconfig/tectonic-worker"
KUBELET_ENV="/etc/kubernetes/kubelet.env"


errmsg () {
cat <<-ERRMSG>&2
	New installs will need to populate the following files:
        ${KUBE_SETTINGS_LOCAL}
        /etc/kubernetes/kubeconfig

ERRMSG
}

egrep -q "^KUBERNETES_DNS_SERVICE_IP=[[:alnum:].]+" ${KUBE_SETTINGS_LOCAL}
ecode=$?

if [ $ecode -gt 0 ]; then
cat <<-DNSERR>&2
	There was a problem validating your DNS service IP in ${KUBE_SETTINGS_LOCAL}
	Refusing to start
DNSERR
	errmsg
	exit 1
fi

egrep -q "^CLUSTER_DOMAIN=[[:alnum:].-]" ${KUBE_SETTINGS_LOCAL}
ecode=$?

if [ $ecode -gt 0 ]; then
cat <<-DNSERR>&2
	There was a problem validating your CLUSTER_DOMAIN in ${KUBE_SETTINGS_LOCAL}"
	Refusing to start"
DNSERR
	errmsg
	exit 1
fi
