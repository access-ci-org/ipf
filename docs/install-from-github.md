# Install from git

1. Get installer
   * ```bash
     curl -o ~/install_ipf.sh https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/go.sh
     ```

1. Run installer
   * ```bash
     bash ~/install_ipf.sh
     ```
   * Note: IPF will be installed into the current directory. All commands in
     this guide assume the current directory is `~/`.

1. Do first time setup
   * ```bash
     bash ~/ipf/bin/prep.sh
     ```
     
# Setup the extmodules workflow
## Configure the extmodules workflow
1. Set variables for your site (for upgrade or re-install, skip this step)
   * ```bash
     cp ~/ipf/etc/configure_extmodules.conf.sample ~/ipf/etc/configure_extmodules.conf
     vim ~/ipf/etc/configure_extmodules.conf
     cp ~/ipf/etc/amqp.conf.sample ~/ipf/etc/amqp.conf
     vim ~/ipf/etc/amqp.conf
     ```
   * Note: for initial testing, leave the PUBLISH variable empty.
1. Run the configure script
   * ```bash
     bash ~/ipf/bin/configure_extmodules
     ```

## Test the extmodules workflow
1. Start the workflow
   * ```bash
     bash ~/ipf/bin/wfm start
     ```
1. Check the output
   * ```bash
     bash ~/ipf/bin/wfm list
     ```
   * Check the `OUTPUT` file that was listed above
1. Stop the workflow
   * ```bash
     bash ~/ipf/bin/wfm stop
     ```

## Test the publishing setup
1. Enable publishing
   * ```bash
     sed -i -e '/PUBLISH=/cPUBLISH=1' ~/ipf/etc/configure_extmodules*.conf
     ```
1. Re-run the configure script
   * ```bash
     bash ~/ipf/bin/configure_extmodules
     ```
1. Start the workflow
   * ```bash
     bash ~/ipf/bin/wfm start
     ```
1. Check the published data
   * Look for the resource name at: https://operations-api.access-ci.org/wh2/state/v1/status/
   * The date in the `Processed at` column should be recent.

# Setup recurring runs for production
1. Create a scheduled task to restart the workflows after a system restart.
   * Example crontab:
     ```bash
        @restart $HOME/ipf/bin/wfm start
     ```


# Errata

## Notes
- This install method currently supports only the `extmodules` workflow.
  Other workflows will be added in the future.

## See also
- [Install from github FAQ](install-from-github-FAQ.md)
