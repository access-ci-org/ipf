#!/bin/bash

INSTALL_DIR=___INSTALL_DIR___
. ${INSTALL_DIR}/lib/utils.sh

BIN="$INSTALL_DIR"/bin
ETC="$INSTALL_DIR"/etc
VENV="$INSTALL_DIR"/.venv
V_PYTHON="$VENV"/bin/python
CONF="$HOME"/.config/ipf


assert_python_minimum_version() {
  [[ $DEBUG -eq $YES ]] && set -x
  SYSTEM_PYTHON=$(which python3) 2>/dev/null
  [[ -z "$SYSTEM_PYTHON" ]] && die "Unable to find Python on this system."
  "$SYSTEM_PYTHON" "$INSTALL_DIR"/assert_py_ver.py || die "Python version is too old."
  success "Python version check passed"
}


mk_venv() {
  [[ $DEBUG -eq $YES ]] && set -x
  [[ -d "$VENV" ]] || {
    "$SYSTEM_PYTHON" -m venv "$VENV"
  }
  success "Python venv created at '$VENV'"
}


install_dependencies() {
  [[ $DEBUG -eq $YES ]] && set -x
  "$V_PYTHON" -m pip install --upgrade pip || die "Pip upgrade had a problem"
  "$V_PYTHON" -m pip install -r "$ETC"/requirements.txt || die "Problem installing dependencies"
  success "Dependencies installed"
}


restore_config_links() {
  [[ $DEBUG -eq $YES ]] && set -x
  /bin/bash "$BIN"/save_configs.sh
}


[[ $DEBUG -eq $YES ]] && set -x

assert_python_minimum_version

mk_venv

install_dependencies

restore_config_links
