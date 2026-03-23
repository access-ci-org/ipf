# Frequently Asked Questions

## INSTALLATION / UPGRADE

### How do I upgrade to the latest version?
1. Run the install script again. The `pip` command will check for a newer
   version and install it.
   * ```bash
     bash ~/ipf-setup.sh
     ```

Note: Check the pip output to verify the new version is installed. If a newer
version is available but it wasn't installed, see the section below: "Pip won't
install the latest version of ipf?".

### How can I start over from scratch?
1. Stop any running workflows
   * ```bash
     bash ~/ipf/bin/wfm stop
     ```

1. Backup config files
   * ```bash
     bash ~/ipf/bin/save_configs.sh
     ```

1. Remove the install directory and script
   * ```bash
     rm -rf ~/ipf ~/ipf-setup.sh
     ```

1. Follow the [Installation Guide](01_install.md) again starting from the top

1. The backed up config files will have been restored. Generate the workflow
   files
   * ```bash
     bash ~/ipf/bin/configure_extmodules
     ```

1. Start the workflows
   * ```bash
     ~/ipf/bin/wfm start
     ```
1. Check the published data
   * See steps in [Configure Software Modules Publishing](03_configure-extmodules-workflow.md)


### Pip won't install the latest version of ipf?
Two possible workarounds:
* `rm -rf ~/ipf/`

OR

* `rm -rf /tmp/pip-build*`

Then re-run the installer.

See also:
https://stackoverflow.com/questions/14617136/why-is-pip-installing-an-old-version-of-my-package

### What version of ipf is currently installed?
```bash
~/ipf/.venv/bin/pip freeze
```


## CONFIGURATION

### Can I configure multiple workflows of the same type?
Yes!  The `configure_extmodules` script will look for config files matching the
naming convention `configure_extmodules*.conf`. You can create multiple config
files and a workflow definition will be created for each one. Just make sure
that `RESOURCE_NAME` is unique in each config file.


### How can I backup my workflow configs?
1. Backup workflow configs
   * ```bash
     bash ~/ipf/bin/save_configs.sh
     ```
This will do 2 things:
* make backup copies in `~/.config/ipf/`
* create symlinks to the backup copies in the ipf install dir.

On a re-install, the IPF installer will look for any backed up
config files and re-make the symlinks.



## TROUBLESHOOTING

### Modules are missing from IPF's published list
Check the permissions on the module lua file. Ipf must be able to read the
module lua file in order to get the data required for publishing.

### Module name is spelled differently than what "module spider" reports
Check the spelling in the module lua file. Ipf reads the module name from the
lua file.

### General troubleshooting hints
* Check the ipf log file for warnings
  1. Log file location is given in the output of `~/ipf/bin/wfm ls`
  1. `grep -F WARNING $(~/ipf/bin/wfm ls | awk '$1=="LOG:" {print $2}')`
* Compare output from module spider with ipf collected data
  1. `mkdir -p ~/ipf/utils`
  1. `pushd ~/ipf/utils`
  1. `curl -O https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/module_spider.sh`
  1. `curl -O https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/utils/ipf_pkgs.sh`
  1. `comm -3 <(./module_spider.sh) <(ipf_pkgs.sh)`
  1. For any unexpected differences:
     1. Check lmod lua file permissions and contents
     1. Check lmod cache file contents and age
  1. `popd ~/ipf/utils`
