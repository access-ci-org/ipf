#!/bin/bash

export QS_GIT_REPO=https://github.com/access-ci-org/ipf.git
# if QS_GIT_BRANCH is not specified, quickstart will try "main" and "master"
#export QS_GIT_BRANCH=CTT-304/aloftus/backwards_compatable
curl https://raw.githubusercontent.com/andylytical/quickstart/main/quickstart.sh | bash
