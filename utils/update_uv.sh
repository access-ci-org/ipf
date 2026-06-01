#!/bin/bash

SRC=https://astral.sh/uv/install.sh

TGT=uv_installer.sh

# --silent \
# --show-error \
curl \
  --location \
  --fail \
  --time-cond "${TGT}" \
  --remote-time \
  --output "${TGT}" \
  "${SRC}"
