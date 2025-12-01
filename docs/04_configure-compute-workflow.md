# Setup the compute workflow
The steps for compute workflow are nearly identical to those for the extmodules
workflow. For the sake of brevity, only the differences are documented here.

1. Create the config file for compute workflow
   * ```bash
     cp -n ~/ipf/etc/configure_compute.conf.sample ~/ipf/etc/configure_compute.conf
     vim ~/ipf/etc/configure_compute.conf
     ```
   * Note: if publishing for multiple resources, make one conf file per
     resource. The filenames must match the glob `configure_compute*.conf`

1. Run the configure script
   * ```bash
     bash ~/ipf/bin/configure_compute
     ```

1. At this point, all the remaining steps are the same as the [extmodules
   workflow](03_configure-extmodules-workflow.md). Follow those instructions again but replace any instance of
`configure_extmodules.conf` -> `configure_compute.conf`.

## Backup the workflow config files
```bash
bash ~/ipf/bin/save_configs.sh
```
