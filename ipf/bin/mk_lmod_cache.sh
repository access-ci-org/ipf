#!/bin/bash

INSTALL_DIR=___INSTALL_DIR___
. ${INSTALL_DIR}/lib/utils.sh


SYSTEM_FILE="${HOME}"/.lmod/mData/system.txt
CACHE_DIR="${HOME}"/.lmod/mData/cacheDir
CACHE_FILE="${CACHE_DIR}"/spiderT.lua


assert_cache_dir() {
  mkdir -p "${CACHE_DIR}"
  [[ -d "${CACHE_DIR}" ]] || die "cache dir not found: '${CACHE_DIR}' "
}


assert_environment() {
  [[ -z "${LMOD_DIR}" ]] && die "LMOD_DIR not defined"
  [[ -d "${LMOD_DIR}" ]] || die "LMDO_DIR not found: '${LMOD_DIR}'"
}


mk_lmod_cache() {
  "${LMOD_DIR}"/update_lmod_system_cache_files \
    -d "${CACHE_DIR}" \
    -t "${SYSTEM_FILE}" \
    $MODULEPATH

  [[ -f "${CACHE_FILE}" ]] || die "cache file not found: '${CACHE_FILE}'"
  [[ -f "${SYSTEM_FILE}" ]] || die "system timestamp file not found: '${SYSTEM_FILE}'"
}


###
# MAIN
###

[[ $DEBUG -eq $YES ]] && set -x

assert_cache_dir

assert_environment

mk_lmod_cache
