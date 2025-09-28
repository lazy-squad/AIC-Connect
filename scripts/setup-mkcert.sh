#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
CERT_DIR=${CERT_DIR:-"${REPO_ROOT}/certs"}
CERT_FILE=${CERT_FILE:-"${CERT_DIR}/localhost.pem"}
KEY_FILE=${KEY_FILE:-"${CERT_DIR}/localhost-key.pem"}

mkdir -p "${CERT_DIR}"

if ! command -v mkcert >/dev/null 2>&1; then
  echo "mkcert is not installed. Visit https://github.com/FiloSottile/mkcert for installation instructions." >&2
  exit 1
fi

if [ ! -f "${CERT_FILE}" ] || [ ! -f "${KEY_FILE}" ]; then
  echo "Generating mkcert certificates in ${CERT_DIR}" >&2
  mkcert -install
  mkcert -cert-file "${CERT_FILE}" -key-file "${KEY_FILE}" localhost 127.0.0.1 ::1
else
  echo "Certificates already exist at ${CERT_DIR}. Delete them to re-create." >&2
fi

ls -al "${CERT_DIR}" | grep localhost || true
