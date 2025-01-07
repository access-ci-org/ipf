# Frequently Asked Questions

## What does `no pid file` mean when starting workflows?
Not sure right now, but just check publishing status at
https://operations-api.access-ci.org/wh2/state/v1/status/
to see if the runs were published.

Also, check local process status with
```bash
bash ~/ipf/bin/wfm status
```


## How do I upgrade to the latest version?
1. Re-run the installer
   * ```bash
     bash ~/install_ipf.sh
     ```


## I messed up the install. Can I start over from scratch?
Yes!
1. Stop any running workflows
   * ```bash
     bash ~/ipf/bin/wfm stop
     ```
1. Make backups of any config files
   * ```bash
     bash ~/ipf/bin/save_configs.sh
     ```
1. Remove the install directory and installer
   * ```bash
     rm -rf ~/ipf install_ipf.sh
     ```
1. Follow through the QUICKSTART guide again starting from the top



## Can I configure multiple workflows of the same type?
Yes!  The `configure_extmodules` script will look for config files matching the
naming convention `configure_extmodules*.conf`. You can create multiple config
files and a workflow definition will be created for each one. Just make sure
that `RESOURCE_NAME` is unique in each config file.


## How can I backup my workflow configs?
1. Backup workflow configs
   * ```bash
     bash ~/ipf/bin/save_configs.sh
     ```
This will do 2 things:
* make backup copies in `~/.config/ipf/`
* create symlinks to the backup copies in the ipf install dir.
On a re-install, the IPF installer will look for any backed up
config files and re-make the symlnks.
