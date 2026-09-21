#!/usr/bin/bash

IPF_PATH=~/ipf
BIN="${IPF_PATH}"/bin
WFM="${BIN}"/wfm


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


get_json_data_file() {
  "${WFM}" ls 2>&1 \
  | awk '/OUTPUT: / && /extended_modules.json/ {print $2}' \
  | head -1
}



get_clean_names() {
  jq \
    '.ApplicationHandle[].Value | split("/")[0] | gsub("^\\s+|\\s+$"; "")' \
    "${JSON_PATH}" \
  | sort -u \
  | tr -d '"'
}


###
# MAIN
###

JSON_PATH=$( get_json_data_file )
[[ -f "${JSON_PATH}" ]] || die 'JSON data file not found'

get_clean_names
