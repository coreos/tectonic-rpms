#!/usr/bin/env bash

trap "fail" ERR
trap "cleanup" EXIT


fail() {
	cat <<-FAILSTATUS >&2
	Failed to produce signed RPM

	Exiting
FAILSTATUS
	cleanup
}

cleanup() {
	if [ -d "${tempdir}" ]; then
		rm -rf "${tempdir}"
	fi
}

rpmfile="${1}"

if [ -z ${rpmfile} ]; then
	cat <<-BLANKRPM >&2dd
	You must supply an RPM file as the sole argument
BLANKRPM
	exit 1
fi
if [ ! -f "${rpmfile}" ]; then
	cat <<-MISSINGRPM >&2
	The rpm file "${rpmfile}" cannot be found
MISSINGRPM
	exit 1
fi

set -o errexit
set -o pipefail
set -o nounset

readonly tempdir="$(mktemp -d /tmp/RPMSIGN-XXXX)"
mkdir -p "${tempdir}"/{gnupg,signtest}
export GNUPGHOME="${tempdir}/gnupg"
chmod 700 "${GNUPGHOME}"

echo "Using temporary directory - ${tempdir}"
grep -q "BEGIN PGP PRIVATE KEY BLOCK" "${BASH_SOURCE%/*}/../signing/RPM-GPG-KEY-Tectonic.secret"  || echo "Could not read GPG key. Run git-crypt unlock." && exit 1

cp "${BASH_SOURCE%/*}/../signing/RPM-GPG-KEY-Tectonic" "${tempdir}/signtest/signing-key.key" 

cat <<-GPGSETTINGS > "${GNUPGHOME}/gpg.conf"
	cert-digest-algo SHA512
	keyid-format 0xlong
	with-fingerprint
GPGSETTINGS

echo -e "\nImporting keys..."
gpg --import "${BASH_SOURCE%/*}/../signing/RPM-GPG-KEY-Tectonic.secret"

echo -e "\nPerforming GPG signature..."
rpmsign -D '_gpg_name 0xCF866CFE16431E6A'  --addsign "${rpmfile}"

echo -e "\nChecking GPG signature..."
rpm -Kv -D "_keyringpath ${tempdir}/signtest" "${rpmfile}" 
#rpm -Kv -D "_keyringpath ${tempdir}/signtest" "${rpmfile}" | grep -5 Signature
echo -e "\nRPM signed successfully"

unset GNUPGHOME
