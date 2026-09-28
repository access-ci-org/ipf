#!/usr/bin/bash

IPF_PATH=~/ipf
BIN="${IPF_PATH}"/bin
WFM="${BIN}"/wfm


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

get_clean_names
