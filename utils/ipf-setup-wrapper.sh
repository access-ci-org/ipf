#!/usr/bin/bash

set -x

# =========================
# customize these as needed
# =========================

# set to an absolute path or leave unset (defaults to $HOME/ipf)
export IPF_INSTALL_DIR=/scratch/user/u.al8635/ipf
# set to "yes" or leave unset (defaults to latest)
export IPF_ALLOW_PRE_RELEASE=yes
# get version string from
#    https://pypi.org/project/ipf/#history      (production releases)
# OR https://test.pypi.org/project/ipf/#history (pre-release versions)
export IPF_INSTALL_VERSION=1.9.9.dev1783568317
# either a branch name or leave unset (defaults to master)
IPF_GIT_BRANCH=ATS-30367
# where to save the installer script
IPF_SETUP="${HOME}"/ipf-setup.sh
# get a list of commands that can be run manually
#MANUAL=yes

# =====================================
# shouldn't need to touch anything else
# =====================================

IPF_BIN="${IPF_INSTALL_DIR}"/bin
VENV="${IPF_INSTALL_DIR}"/.venv
URL_BASE='https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads'
IPF_SETUP_URL="${URL_BASE}"/"${IPF_GIT_BRANCH:-master}"/setup.sh
ACTION="${MANUAL:+echo}"

[[ -d "${IPF_BIN}" ]] && {
  ${ACTION}" bash "${IPF_BIN}"/wfm stop
  ${ACTION}" rm -rf "${IPF_INSTALL_DIR}"/
}

${ACTION}" rm -f "${IPF_SETUP}"

${ACTION}" curl -o "${IPF_SETUP}" "${IPF_SETUP_URL}"

${ACTION}" bash "${IPF_SETUP}"

${ACTION}" "${VENV}"/bin/python --version

${ACTION}" "${VENV}"/bin/python -m pip freeze
