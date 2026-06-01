#!/bin/bash

YES=0 #no touchee
NO=1  #no touchee


# ###
# User might want to change these, though should use environment vars

INSTALL_DIR="${IPF_INSTALL_DIR:-$HOME/ipf}"
DEBUG=$YES
VERBOSE=$YES

# END OF USER CONFIGURABLE SECTION
# ###


# NO USER CHANGES AFTER THIS

export UV_PYTHON=3.9 #python version required by IPF
UV_DIR="${INSTALL_DIR}"/uv
UV="${UV_DIR}"/uv
VENV="$INSTALL_DIR"/.venv
V_PYTHON="$VENV"/bin/python
SITE_PACKAGES=  #created by mk_venv()
IPF_PATH=       #created by mk_venv()
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No Color


err() {
	echo -e "${RED}✗ ERROR: $*${NC}"
}


success() {
  echo -e "${GREEN}✓ $*${NC}"
}


die() {
  err "$*"
  echo "from (${BASH_SOURCE[1]} [${BASH_LINENO[0]}] ${FUNCNAME[1]})"
  kill 0
  exit 99
}


log() {
  [[ $VERBOSE -eq $YES ]] || return 0
  echo "INFO $*" >&2
}


debug() {
  [[ $DEBUG -eq $YES ]] || return 0
  echo "DEBUG (${BASH_SOURCE[1]} [${BASH_LINENO[0]}] ${FUNCNAME[1]}) $*"
}


install_uv() {
  [[ $DEBUG -eq $YES ]] && set -x
  [[ -f "${UV}" ]] || {
    export UV_UNMANAGED_INSTALL="${UV_DIR}"
    UV_URL=https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/uv_installer.sh
    [[ -n "${IPF_UV_URL}" ]] && UV_URL="${IPF_UV_URL}"
    UV_INSTALLER="${UV_DIR}"/uv_installer.sh
    curl -LsSf --create-dirs "${UV_URL}" -o "${UV_INSTALLER}"
    sh "${UV_INSTALLER}" || die 'failed to install uv'
  }
}


mk_venv() {
  [[ $DEBUG -eq $YES ]] && set -x
  [[ -d "$VENV" ]] || {
    export UV_PYTHON_INSTALL_DIR="${UV_DIR}"/python
    export UV_NO_CACHE=1
    export UV_MANAGED_PYTHON=1
    "$UV" venv "$VENV"
    success "Python venv created at '$VENV'"
    "${V_PYTHON}" -m ensurepip
    success "Ensure native pip is available"
    "${V_PYTHON}" -m pip install --upgrade pip
    success "Updated to latest pip version"
  }
  SITE_PACKAGES=$(
    "$V_PYTHON" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'
  )
  IPF_PATH="$SITE_PACKAGES"/ipf
}


is_pre_release_allowed() {
  # to install the latest pre-release version: export IPF_ALLOW_PRE_RELEASE=yes
  [[ $DEBUG -eq $YES ]] && set -x
  local _retval=$NO
  if [[  "$IPF_ALLOW_PRE_RELEASE" == "yes" \
      || "$IPF_ALLOW_PRE_RELEASE" == "YES" \
      || "$IPF_ALLOW_PRE_RELEASE" == "Y" \
      || "$IPF_ALLOW_PRE_RELEASE" == "y" \
      || "$IPF_ALLOW_PRE_RELEASE" -eq 1
     ]] ; then
     _retval=$YES
   fi
  return $_retval
}


install_ipf_pre_release() {
  [[ $DEBUG -eq $YES ]] && set -x
  is_pre_release_allowed || return
  "${V_PYTHON}" -m pip install \
    --upgrade \
    --no-cache-dir \
    --pre \
    --no-deps \
    --index-url https://test.pypi.org/simple/ \
    ipf \
    && success "Installed dev version of ipf"
}


install_ipf() {
  [[ $DEBUG -eq $YES ]] && set -x
  "${V_PYTHON}" -m pip install \
    --upgrade \
    ipf \
    && success "Ipf and dependencies installed"
}

update_files() {
  [[ $DEBUG -eq $YES ]] && set -x
  # Update any files that need INSTALL_DIR
  local _pattern='___INSTALL_DIR___'
  local _replacement="$INSTALL_DIR"
  grep -r --files-with-matches -F "$_pattern" "$IPF_PATH" \
  | while read; do
      sed -i -e "s?$_pattern?$_replacement?" "$REPLY"
    done
}


mk_symlinks() {
  [[ $DEBUG -eq $YES ]] && set -x
  pushd "$INSTALL_DIR"
  local _symlink_dirs=( bin etc configure lib var )
  for d in "${_symlink_dirs[@]}"; do
    [[ -L $d ]] || ln -s "$IPF_PATH"/$d
  done
  popd
  pushd "$INSTALL_DIR"/bin
  ln -s "${V_PYTHON}"
  popd
}


restore_config_links() {
  [[ $DEBUG -eq $YES ]] && set -x
  /bin/bash "$INSTALL_DIR"/bin/save_configs.sh
}


[[ $DEBUG -eq $YES ]] && set -x

install_uv

mk_venv

install_ipf_pre_release #won't do anything if pre-release is not allowed

install_ipf

update_files

mk_symlinks

restore_config_links
