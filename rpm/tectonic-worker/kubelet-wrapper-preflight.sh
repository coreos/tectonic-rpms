#!/bin/bash
set +o pipefail
set +o nounset
set +o errexit

KUBE_SETTINGS_LOCAL="/etc/kubernetes/kubesettings-local.env"
KUBELET_ENV="/etc/kubernetes/kubelet.env"


errmsg () {
cat <<-ERRMSG> /dev/stderr
	New installs will need to populate the following files:
        ${KUBE_SETTINGS_LOCAL}
        /etc/kubernetes/kubeconfig

ERRMSG
}

egrep -q "^KUBERNETES_DNS_SERVICE_IP=[[:alnum:].]+" ${KUBE_SETTINGS_LOCAL}
ecode=$?

if [ $ecode -gt 0 ]; then
cat <<-DNSERR> /dev/stderr
	There was a problem validating your DNS service IP in ${KUBE_SETTINGS_LOCAL}
	Refusing to start
DNSERR
	errmsg
	exit 1
fi

egrep -q "^CLUSTER_DOMAIN=[[:alnum:].-]" ${KUBE_SETTINGS_LOCAL}
ecode=$?

if [ $ecode -gt 0 ]; then
cat <<-DNSERR> /dev/stderr
	There was a problem validating your CLUSTER_DOMAIN in ${KUBE_SETTINGS_LOCAL}"
	Refusing to start"
DNSERR
	errmsg
	exit 1
fi
