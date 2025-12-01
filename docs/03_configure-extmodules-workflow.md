# Setup the extmodules workflow
## Configure the extmodules workflow
1. Set variables for your site (SKIP this step if upgrading or re-installing)
   * ```bash
     cp -n ~/ipf/etc/configure_extmodules.conf.sample ~/ipf/etc/configure_extmodules.conf
     ```
   * ```bash
     vim ~/ipf/etc/configure_extmodules.conf
     ```
   * NOTE: Usually don't actually have to do anything unless setting up for multiple
     resources from the same host.
   * NOTE: if publishing for multiple resources:
     * Ensure `RESOURCE_NAME` is unique for each extmodules workflow.
     * Make one conf file per resource. The filenames must match the glob `configure_extmodules*.conf`

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
     sed -i -e '/PUBLISH=/cPUBLISH=1' ~/ipf/etc/common.conf
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

At this point, the publishing runs will continue running and reporting once
a day until stopped manually or the system is rebooted.

## Backup the workflow config files
```bash
bash ~/ipf/bin/save_configs.sh
```

## Next - configure job queue publishing
Next: [Configure job queue publishing](04_configure-compute-workflow.md)

# Setup recurring runs for production

1. Create a scheduled task to restart the workflows after a system restart.
   * Example crontab:
     ```bash
        @restart $HOME/ipf/bin/wfm start
     ```
