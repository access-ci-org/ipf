# Install
1. Get the setup script
    ```
    curl -o ~/ipf-setup.sh https://raw.githubusercontent.com/access-ci-org/ipf/refs/heads/master/setup.sh
    ```

1. Run the setup script
    ```
    bash ~/ipf-setup.sh
    ```
Installs into `~/ipf`.

Next: [First time setup](02_configure-common.md)

# Advanced

## Custom Options
To enable one or more custom options, set the indicated environment variable(s)
BEFORE running `ipf-setup.sh`.

### Customize installation dir
* `export IPF_INSTALL_DIR=<PATH_TO_INSTALL_DIR>`

### Pin version of IPF to install
* `export IPF_INSTALL_VERSION=<VERSION_STRING>`

### Install a development version from test.pypi.org
* `export IPF_ALLOW_PRE_RELEASE=yes`
