#!/usr/bin/bash

INSTALL_DIR=___INSTALL_DIR___

. ${INSTALL_DIR}/lib/utils.sh

find_module() {
  local _type
  _type=$( type -t module )
  case "${_type}" in
    function) MODULE=module;;
    file)
      MODULE=$( which module )
      [[ -x "${MODULE}" ]] || die "module command '${MODULE}' not executable"
      ;;
    *) die 'module command not found'
  esac
}

JQ=$( which jq )
[[ -x "${JQ}" ]] || die 'jq command not found'

TMP=$(mktemp)

module_config_as_json() {
  # module config prints output on stderr, so have be careful when gathering it
  [[ -s "${TMP}" ]] \
  || "${MODULE}" --config_json 1>/dev/null 2>"${TMP}"
  # skip any non-json lines from the file
  cat "${TMP}" | sed -e '/^[^{]/ d'
}


version_info() {
  echo "LMOD Version Info"
  echo "-----------------"
  module_config_as_json \
  | "${JQ}" '.configT | {lmodV, tcl_version, luaV}'
}


cache_info() {
  echo "LMOD Cache Info"
  echo "---------------"
  module_config_as_json \
  | "${JQ}" '.cache | flatten | .[]'
}


cleanup() {
  rm -f "${TMP}"
}

###
# MAIN
###

find_module

version_info

cache_info

cleanup
