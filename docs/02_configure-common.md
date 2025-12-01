# One-time Setup
## Configure amqp settings
1. Configure amqp settings
   * ```bash
     cp -n ~/ipf/etc/amqp.conf.sample ~/ipf/etc/amqp.conf
     ```
   * ```bash     
     vim ~/ipf/etc/amqp.conf
     ```
    * NOTE: `amqp.conf` is used for all workflows, so only need to set it up once

## Configure common settings
1. Configure common settings
   * ```bash
     cp -n ~/ipf/etc/common.conf.sample ~/ipf/etc/common.conf
     ```
   * ```bash     
     vim ~/ipf/etc/common.conf
     ```
    * NOTE: `common.conf` is used for all workflows, so only need to set it up once
    * NOTE: `RESOURCE_NAME` is required.
    * NOTE: for initial testing, leave the `PUBLISH` variable empty.

## Backup the config files
```bash
bash ~/ipf/bin/save_configs.sh
```

## Next - Setup the extmodules workflow
Next: [Setup the extmodules workflow](03_configure-extmodules-workflow.md)
