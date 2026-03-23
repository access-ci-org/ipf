#!/usr/bin/bash

set -x

# =========================
# customize these as needed
# =========================

# where to save the installer script
IPF_SETUP="${HOME}"/ipf-setup.sh

# set to an absolute path (default is $HOME/ipf)
IPF_INSTALL_DIR="${HOME}"/ipf

# dont actually do anything, just print out a list of commands
# that can be run manually
# MANUAL=yes

# set to "yes" or leave unset (defaults to latest)
# IPF_ALLOW_PRE_RELEASE=yes

# specify an exact version of IPF
# get version string from
#    https://pypi.org/project/ipf/#history      (production releases)
# OR https://test.pypi.org/project/ipf/#history (pre-release versions)
# IPF_INSTALL_VERSION=1.9.9.dev1783568317

# either a branch name or leave unset (defaults to master)
# IPF_GIT_BRANCH=ATS-30367

# specify a specific version of python if needed
# IPF_UV_PYTHON=3.12

# =====================================
# shouldn't need to touch anything else
# =====================================


[[ -z "${IPF_GIT_BRANCH}" ]] && IPF_GIT_BRANCH=master
URL_BASE='https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads'
IPF_SETUP_URL="${URL_BASE}"/"${IPF_GIT_BRANCH}"/setup.sh
IPF_UV_URL="${URL_BASE}"/"${IPF_GIT_BRANCH}"/utils/uv_installer.sh
IPF_BIN="${IPF_INSTALL_DIR}"/bin
VENV="${IPF_INSTALL_DIR}"/.venv

###
# MAIN
###

# make exports (used by setup script)
export IPF_UV_URL
export IPF_INSTALL_DIR
[[ -n "${IPF_ALLOW_PRE_RELEASE}" ]] && export IPF_ALLOW_PRE_RELEASE
[[ -n "${IPF_UV_PYTHON}" ]] && export IPF_UV_PYTHON
[[ -n "${IPF_INSTALL_VERSION}" ]] && export IPF_INSTALL_VERSION

# set ACTION if doing manual run
if [[ -n "${MANUAL}" ]] ; then
  ACTION=echo
  set +x
  echo 'COMMANDS THAT WOULD HAVE BEEN RUN'
  echo '---------------------------------'
fi

# stop anything running
[[ -x "${IPF_BIN}"/wfm ]] && ${ACTION} bash "${IPF_BIN}"/wfm stop

# cleanup any existing installs
${ACTION} rm -rf "${IPF_INSTALL_DIR}"
${ACTION} rm -rf "${HOME}"/.cache/pip
${ACTION} rm -f "${IPF_SETUP}"

# get new setup script
${ACTION} curl -o "${IPF_SETUP}" "${IPF_SETUP_URL}"
# and run it
${ACTION} bash "${IPF_SETUP}"

# validate install
${ACTION} "${VENV}"/bin/python --version
${ACTION} "${VENV}"/bin/python -m pip freeze
