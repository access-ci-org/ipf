#!/usr/bin/bash

YES=0
NO=1

VERBOSE=$YES
DEBUG=$YES

# ANSI escape codes for colors
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

info() {
  [[ $VERBOSE -eq $YES ]] && {
    echo -e "${RED}INFO: ${NC}$*" 1>&2
  }
}

debug() {
  [[ $DEBUG -eq $YES ]] && {
    echo -e "${RED}DEBUG: ${NC}$*" 1>&2
  }
}


set_jq() {
  [[ $DEBUG -eq $YES ]] && set -x
  JQ=$( which jq )
  [[ -x "${JQ}" ]] || die 'JQ not found'
}


set_lmod_vars() {
  if [[ -z "${MODULESHOME}" ]] ; then
    # module command prints on stderr and so does debug output
    # so write module output to a file, then post-process with awk
    set +x
    module --config_json 2>tee module_config_json 1>/dev/null
    LMOD_PREFIX=$(
      awk '/^+/ {next};  /^\{/ {print};' module_config_json \
      | "${JQ}" -r '.configT.prefix' \
      | tr -d '"'
    )
    [[ $DEBUG -eq $YES ]] && set -x
    [[ -d "${LMOD_PREFIX}" ]] || die "lmod prefix '${LMOD_PREFIX}' not a dir"
    # LMOD_PREFIX=$( module --config_json 2>&1 | "${JQ}" '.configT.prefix' | tr -d '"' )
    MODULES_HOME="${LMOD_PREFIX}"/lmod/lmod
  fi
  LMOD_EXEC="${MODULESHOME}"/libexec
  LMOD_CACHE_UPDATER="${LMOD_EXEC}"/update_lmod_system_cache_files
  [[ -f "${LMOD_CACHE_UPDATER}" ]] || die 'lmod cache update script not found'
  [[ -x "${LMOD_CACHE_UPDATER}" ]] || die 'lmod cache update script not executable'
}


update_lmod_cache() {
  [[ $DEBUG -eq $YES ]] && set -x
  [[ -z "${MODULEPATH}" ]] && die 'empty MODULEPATH'
  local _cache_dir _timestamp_fn
  _cache_dir="${HOME}"/lmod_cache
  _timestamp_fn="${HOME}"/lmod_cache.timestamp
  mkdir -p "${_cache_dir}"
  "${LMOD_CACHE_UPDATER}" \
  -d "${_cache_dir}" \
  -t "${_timestamp_fn}" \
  "${MODULEPATH}"
}


###
# MAIN
###

[[ $DEBUG -eq $YES ]] && set -x

set_jq

set_lmod_vars

update_lmod_cache
