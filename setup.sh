#!/bin/bash

# DO NOT RUN THIS BY HAND
# This file is for use by https://github.com/andylytical/quickstart

INSTALL_DIR="$(pwd)" #this is the directory the user invoked quickstart
BASE=$(readlink -e $( dirname $0 ) )
IPF_SRC="$BASE/ipf"
TS=$(date +%s)
YES=0
NO=1
DEBUG=$YES
VERBOSE=$YES


die() {
  echo "ERROR $*" >&2
  kill -s TERM $BASHPID
  exit 99
}


log() {
  [[ $VERBOSE -eq $YES ]] || return
  echo "INFO $*" >&2
}


debug() {
  [[ $DEBUG -eq $YES ]] || return
  echo "DEBUG (${BASH_SOURCE[1]} [${BASH_LINENO[0]}] ${FUNCNAME[1]}) $*"
}


update_files() {
  [[ $DEBUG -eq $YES ]] && set -x
  # Update any files that need INSTALL_DIR
  local _pattern='___INSTALL_DIR___'
  local _replacement="$INSTALL_DIR/ipf"
  grep -r --files-with-matches -F "$_pattern" "$BASE" \
  | while read; do
      sed -i -e "s?$_pattern?$_replacement?" "$REPLY"
    done
}


install_common() {
  [[ $DEBUG -eq $YES ]] && set -x
  rsync -v --recursive \
    -b --suffix=."$TS" \
    --checksum \
    --exclude-from="$BASE"/setup.excludes \
    "$IPF_SRC" \
    "$INSTALL_DIR"
}


install_special() {
  [[ $DEBUG -eq $YES ]] && set -x
  rsync -v --recursive \
    --ignore-existing \
    --include-from="$BASE"/setup.excludes \
    "$IPF_SRC" \
    "$INSTALL_DIR"
}

[[ $DEBUG -eq $YES ]] && set -x

update_files

install_common

install_special
