# IPF Utils
Helpful utility scripts.

# Usage

## Compare IPF packages with those from LDOD module spider cmd
* `curl -o
  https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/ls_pkgs_ipf.sh`
* `curl -o
  https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/ls_pkgs_spider.sh`
* `comm -3 <(bash ls_pkgs_spider.sh) <(bash ls_pkgs_ipf.sh)`


## Make a personal lmod cache
Useful to run a test install of IPF using a local lmod cache
(if no system level cache is available)

LMOD cache will be written to ${HOME}/lmod_cache/*
* `curl -O 
  https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/mk_lmod_cache.sh`
* `bash mk_lmod_cache.sh`

### Configure IPF to use the local LMOD cache from above
* `sed -e "/^LMOD_CACHE_FILE=/
  c LMOD_CACHE_FILE=${HOME}/lmod_cache/spiderT.lua"
"${HOME}"/ipf/etc/configure_extmodules.conf`
* `"${HOME}"/ipf/bin/configure_extmodules`

## IPF Easy Install
* `curl -O 
  https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/ipf-setup-wrapper.sh`
* `vim ipf-setup-wrapper.sh`
  * Review variables at the top of the script, change any for your site.
* `bash ipf-setup-wrapper.sh`

# Internal only
* `update_uv.sh` used by IPF setup script
* `uv_installer.sh` used by IPF Easy Install script
