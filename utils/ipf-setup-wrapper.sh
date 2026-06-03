#!/usr/bin/bash

set -x

IPF_BIN="${HOME}"/ipf/bin
VENV="${HOME}"/ipf/.venv
IPF_SETUP="${HOME}"/ipf-setup.sh

[[ -z "${IPF_GIT_BRANCH}" ]] && {
  echo "Missing environment variable IPF_GIT_BRANCH"
  exit 1
}
URL_BASE='https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads'
IPF_SETUP_URL="${URL_BASE}"/"${IPF_GIT_BRANCH}"/setup.sh

bash "${IPF_BIN}"/wfm stop

rm -rf ~/ipf

rm -f "${IPF_SETUP}"

curl -o "${IPF_SETUP}" "${IPF_SETUP_URL}"

export IPF_UV_URL="${URL_BASE}"/"${IPF_GIT_BRANCH}"/utils/uv_installer.sh
export IPF_ALLOW_PRE_RELEASE=yes

bash "${IPF_SETUP}"

"${VENV}"/bin/python --version

"${VENV}"/bin/python -m pip freeze
