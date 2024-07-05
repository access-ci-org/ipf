# access-ci-org/ipf %VER%-%REL%
=====================


## Quickstart
===========================================

### What is IPF?


IPF is a Python program that gathers resource information, formats it in a [GLUE2 standard format (5)](#glue2), and publishes it
to a RabbitMQ service. IPF is configured to run one or more “workflows” each defining the steps that IPF executes to collect,
format, and publish a specific type of resource information.


## Pre-requisites
--------------

### Preparing to Install IPF
-------------------------


-   Before installing IPF operators should register their cluster resource in [CiDeR (4)](#CIDER).
    While IPF is capable of publishing information for resources not in CiDeR, ACCESS needs resource
    descriptions in CiDeR to complement the information published with IPF.


-   Identify a single server to run IPF -- a single IPF instance can be used to publish information for multiple resources.


-   To install IPF on a cluster that presents publicly as multiple resources please review this document:
    [Publishing Software for multiple Resources from a single IPF deployment](https://docs.google.com/document/d/1UXF_pwwZdycuUiV7JToKOKMOHNs6VWjdMWFOjUyKMU4/edit?usp=sharing)

-   Decide what installation method to use: 
    *     RPM is recommended for production installs, as it is managed by system tools, and creates an "xdinfo" user to run the workflows.
    *     Pip is easier for installs where root access is not available, though some additional environment variables will need to be set.

-   If you already have an older IPF create a backup of the /etc/ipf working configurations:

    $ tar -cf ipf-etc-yyyymmdd.tar /etc/ipf


### Software Dependencies


-   Python 3.6 or newer 
        (Python 3.11 is implicitly required by the RPM as its site-packages
         are within a python3.11 directory)
-   The python-amqp package
-   The python-setuptools package IF installed by RPM.

*These dependencies are encoded in the RPM.*

### How is an IPF workflow defined?


Each IPF workflow consists of a series of "steps" with inputs, outputs, and dependencies. The steps for each workflow are defined
in one or more JSON formatted files. Workflow JSON files can incorporate other workflow JSON files: for example,
the `<resource>_services_periodic.json` workflow contains one step, which is the `<resource>_services.json` workflow.


IPF workflows are typically defined by JSON files under $IPF_ETC_PATH/ipf/workflow/, particularly in $IPF_ETC_PATH/ipf/workflow/glue2.


### How is an IPF workflow invoked?


To run a workflow execute the ipf_workflow program passing it a workflow definition file argument, like this:


    $INSTALL_DIR/ipf-VERSION/ipf/bin/ipf_workflow <workflow.json>


Workflow JSON files are specified relative to $IPF_ETC_PATH, for example:
`ipf_workflow sysinfo.json`
`ipf_workflow glue2/<resource>_services.json`


Part of workflow configuration includes generating $IPF_ETC_PATH/ipf/init.d scripts to run a workflow periodically.
These scripts are usually copied to the system /etc/init.d directory during installation.


### Which workflows should I configure and run?


The following workflows are recommended for the listed scenarios.

Batch System workflow (compute workflow): *clusters with batch systems*

Software Module workflow: *clusters with command line software modules*

Network Accessible Services workflow: *clusters with with edge services like openssh*

Batch Scheduler Job Event workflow (activity workflow): *clusters that want to support live job event subscriptions*


### Batch System workflow requirements


-   The command line programs for your batch scheduler must be executable.


### Software Modules workflow requirements


-   The module or Lmod files must be readable.


### Network Services workflow requirements


-   The service definition files must be readable, and in a single directory. 
    See Configuring.Service.Files.md for more information


### Batch Scheduler Job Events workflow requirements


-   The batch scheduler log file or directory must be readable on the server where IPF is running and by the user running IPF.
-   The batch scheduler must be logging at the right level for the IPF code to be able to parse the events.
    See the Configuring Torque Logging section.




## Installing IPF
--------------


There are two recommended ways to install IPF: you can use pip install, or you can install from ACCESS RPMs.  The RPMs can be found in the github releases, or 
in the repositories at software.operations.access-ci.org/production.

Installing IPF from RPMs will put it in the directories /usr/lib/python-`<VERSION>`/site-packages/ipf, /etc/ipf, /var/ipf).

To install to an alternate location we recommend using pip.


### PIP installation


To install using pip, you need to have the pip package installed in an appropriate version of Python (3.6+).
We recommend using venv to manage Python installations. More information on venv is available at
<https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>

Depending on how many python versions are in place on your system, "pip" may or may not refer to the python 3 version.
"pip3" should always unambiguously refer to a python3 version of pip.

Once you have a Python 3.6 environment (whether venv or not), to install execute:


    $ pip3 install ipf


When installing via pip: unlike in an RPM install, the files get
installed relative to your Python installation (whether in a virtualenv
or system Python). Notably, ipf_configure and ipf_workflow end
up in the virtualenv's bin directory, and the location IPF expects to
find as its IPF_ETC_PATH (/etc/ipf in an RPM install) is relative to
the Python site-packages directory.


You can find your site-packages path for the Python you used for the pip install with: 


     $ python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'


When running any IPF commands by hand in a pip install, you will need to
set the environment variable IPF_ETC_PATH. Its value should be the
site-packages directory referenced above, plus "/etc/ipf". For a system
Python, this might look something like
"/usr/lib/python3.6/site-packages/etc/ipf". 

If you have run ipf_configure to set up your workflows, and chosen the
recommended base directory, your workflow definitions will have the
appropriate IPF_ETC_PATH defined in them.

If you wish to have the workflows run as a user other than the one that 
performed the pip install, you will have to do so manually.


### RPM Installation


Note(s): - The RPM will automatically create an "xdinfo" account that
will own the install and that will execute the workflows via sudo.


Steps: 1) Download the latest RPM from the IPF releases at GitHub:
https://github.com/access-ci-org/ipf/releases


2)  Install ipf


    $ yum install ./ipf-%VER%-%REL.noarch.rpm




## Updating a previous IPF installation
------------------------------------


The JSON files that have been written by previous runs of
ipf_configure would, in some previous versions of IPF get
overwritten by subsequent runs of ipf_configure. This is no
longer the case--previous versions get backed up, not overwritten. They
will *not* be erased by removing OR updating the package (nor will the
service files copied to /etc/init.d be erased).


To perform the update to the latest RPM distribution of ipf:

1.  get the latest RPM from https://github.com/access-ci-org/ipf/releases
2.  $ sudo yum update ./ipf-%VER%-%REL.noarch.rpm
3.  If there are new workflows you need to configure, follow the
    configuration steps as outlined in the Configuration section below.


## Configuring IPF
---------------


To make configuration easier, an `ipf_configure` script is
provided in the bin directory (in /usr/bin if you installed RPMs,
otherwise in $INSTALL_DIR/ipf-VERSION/ipf/bin). This script will 
generate workflow definition files and example init files. 


If you intend to publish software module information via the extmodules 
workflow, set the environment variable MODULEPATH
to point to the location of the module files before running
ipf_configure. If you intend to publish the service workflow
set SERVICEPATH to point to the location of the service definition files
before running ipf_configure (more on this below).
As of IPF v 1.7, ipf_configure accepts command line parameters
to tell it which workflows to configure, and with which options.


An invocation of ipf_configure on a resource that has installed 
IPF using RPM and wants to publish software information might look like:


/usr/bin/ipf_configure --rpm --resource_name <RESOURCE_NAME> --workflows=extmodules --publish --amqp_certificate /etc/grid-security/cert_for_ipf.pem --amqp_certificate_key /etc/grid-security/key_for_ipf.pem  --modulepath /path/to/modules --lmod_cache_file /path/to/lmodcache.lua


These options mean:


--rpm        IPF was installed using RPM; this lets us know where files should be on disk


--resource_name        The name of your resource.   To find your resource name, 
            go to "https://operations.access-ci.org/resources/access-allocated"
            to find your resource, and use the "Global Resource ID" value.

--workflows           Comma delimited list of workflows to configure.  Values can include:
                             compute, activity, extmodules, services
--publish        Necessary if you wish to configure your workflow to publish to ACCESS's
                                      AMQP service for inclusion in Information Services


--amqp_certificate        The path to the certificate to use to authenticate with ACCESS’s AMQP


--amqp_key                  The path to the key for your certificate


--modulepath                The MODULEPATH where the modulefiles for software publishing are 
                                    found.  If not specified $MODULEPATH from the user environment
                                    will be used.
--lmod_cache_file           The location of an lmod cache file that contains exactly the set of modules you wish to publish.  If you do not specify an lmod_cache_file, IPF will fall back to its traditional behavior of walking the MODULEPATH.


Other common options:


--amqp_username          If not using certificates to authenticate, use these to specify 
--amqp_password           username and password


--pip         IPF was installed using “pip install”


For a full list of command line options, please try


$ ipf_configure ----help


-   `ipf_configure` should be run as the user that will run the
    information gathering workflows

-    You must always specify --resource_name, and you should use the 
     "Global Resource ID" from 
     https://operations.access-ci.org/resources/access-allocated 


-   The preferred way to authenticate is via an X.509 host certificate
    and key. You can place these files wherever you like, but the
    default locations are /etc/grid-security/xdinfo-hostcert.pem and
    /etc/grid-security/xdinfo-hostkey.pem. These files must be readable
    by the user that runs the information gathering workflows.


-   Submit an ACCESS ticket to authorize your server to publish ACCESS's
    RabbitMQ services. If you will authenticate via X.509, include the
    output of 'openssl x509 -in path/to/cert.pem -nameopt RFC2253
    -subject -noout' in your ticket. If you will authenticate via
    username and password, state that and someone will contact you.


Note: The xdinfo user as created by the ipf rpm installation has
/bin/nologin set as its shell by default. This is because for most
purposes, the xdinfo user doesn't need an interactive shell. However,
for some of the initial setup, it is easiest to use the xdinfo user with
an interactive shell (so that certain environment variables like
MODULEPATH can be discovered.) Thus, it is recommended that the
configuration steps are run after something like the following:


    $ sudo -u xdinfo -s /bin/bash --rcfile /etc/bashrc -i
    $ echo $MODULEPATH
    $ echo $SERVICEPATH


Execute:


    $ ipf_configure \<command line options shown above\>



If you encounter any errors or the script does not cover your situation,
Please submit an ACCESS ticket.


When the script exits, the etc/ipf/workflow/glue2/ directory will
contain a set of files RESOURCE_NAME_*.json that describe the
information gathering workflows you have configured and etc/ipf/init.d
will contain ipf-RESOURCE_NAME_* files which are the init scripts you
have configured.


As root, copy the etc/ipf/init.d/ipf-RESOURCE_NAME-* files into
/etc/init.d. Your information gathering workflows can then be enabled,
started, and stopped in the usual ways. You may need to perform a
'chkconfig --add' or equivalent for each service.


## Software Module Publishing Best Practices
-----------------------------------------


The IPF Software Module workflow publishes information about locally
installed software available through modules or Lmod. IPF tries to make
intelligent inferences from the system installed modules files when it
publishes software information. There are some easy ways, however, to
add information to your module files that will enhance/override the
information otherwise published.


The ExtModules workflow, as of IPF 1.8 has two methods for discovering the 
modules you wish to publish.  The recommended method, for any site using Lmod, 
is to point the workflow at an lmod cache file that represents exactly what
you wish to publish.  It will then publish every module in the spiderT table
from the cache file, except modules listed in the hiddenT table.

If you are not using Lmod, or do not wish to use lmod cache files, the
workflow will fall back to the traditional method of walking the MODULEPATH.
The workflow then traverses your MODULEPATH and infers fields such
as Name and Version from the directory structure/naming conventions of
the module file layout. The new IPF default behavior is to treat each 
directory in your MODULEPATH as a top level directory, under which all of
the subdirectory structure is semantically significant (and part of the
inferred name of the module).  The old default behavior, if desired, can be
enabled with by configuring the extmodules workflow with the --modules_recurse
argument.

Depending on the exact workflow steps, fields such as Description may be 
blank, or inferred from the stdout/stderr text of the module. However, the 
following fields can always be explicitly added to a module file:

    Name:
    Version:
    Description:
    URL:
    Category:
    Keywords:
    SupportStatus:
    SupportContact:


Each field is a key: value pair. The IPF workflows are searching the
whole text of each module file for these fields. They may be placed in a
module-whatis line, or in a comment, and IPF will still read them.

More details about the contents of these fields can be found in the more
comprehensive INSTALL.md documentation.


## Testing
-------


1)  To test the extended attribute modules workflow, execute:


    # service ipf-RESOURCE_NAME-glue2-extmodules start


This init script starts a workflow that periodically gathers (every hour
by default) and publishes module information containing extended
attributes.


The log file is in /var/ipf/RESOURCE_NAME_modules.log (or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_extmodules.log) and should
contain messages resembling:


    2013-05-30 15:27:05,309 - ipf.engine - INFO - starting workflow extmodules
    2013-05-30 15:27:05,475 - ipf.publish.AmqpStep - INFO - step-3 - publishing representation ApplicationsOgfJson of Applications expanse.sdsc.access-ci.org
    2013-05-30 15:27:05,566 - ipf.publish.FileStep - INFO - step-4 - writing representation ApplicationsOgfJson of Applications expanse.sdsc.access-ci.org
    2013-05-30 15:27:06,336 - ipf.engine - INFO - workflow succeeded


If any of the steps fail, that will be reported and an error message and
stack trace should appear. Typical failures are caused by the
environment not having specific variables or commands available.


This workflow describes your modules as a JSON document containing GLUE
v2.0 Application Environment and Application Handle objects. This
document is published to the ACCESS RabbitMQ service in step-3 and is
written to a local file in step-4. You can examine this local file in
/var/ipf/RESOURCE_NAME_apps.json. If you see any errors in gathering
module information, please submit an ACCESS ticket.

