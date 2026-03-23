#!/usr/bin/bash

SHOW_HIDDEN=

ENDWHILE=0
while [[ $# -gt 0 ]] && [[ $ENDWHILE -eq 0 ]] ; do
  case $1 in
    -s) SHOW_HIDDEN='--show_hidden';;
    --) ENDWHILE=1;;
    -*) echo "Invalid option '$1'"; exit 1;;
     *) ENDWHILE=1; break;;
  esac
  shift
done

module --redirect --terse ${SHOW_HIDDEN} spider \
| awk -F'/' '/\/$/ {print $1}' \
| sort -u
