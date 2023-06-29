# access-ci-org/ipf %VER%-%REL%
=====================


## Installation and Configuration Instructions
===========================================


## What does IPF do?
------------


The *Information Publishing Framework* ["IPF" (1)](#IPF) is a generic framework used by resource operators to gather and publish
dynamic resource information in [GLUE 2 serialized format](http://www.ogf.org/documents/GFD.147.pdf). IPF can publish four types
of resource information: 1) Batch system configuration and queue contents, 2) Software Modules available from the command line,
3) Network services information, and 4) Batch scheduler job events.

Campuses and other research resource operators that are not affiliated with ACCESS-CI are welcome to use IPF. All information
published using IPF is available to portals and to science gateways through ACCESS Operations APIs.

This document describes how to install and configure IPF.


## How does IPF Work?
------------------


### What is IPF?


IPF is a Python program that gathers resource information, formats it in a [GLUE2 standard format (5)](#glue2), and publishes it
to a RabbitMQ service. IPF is configured to run one or more “workflows” each defining the steps that IPF executes to collect,
format, and publish a specific type of resource information.


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


## Pre-requisites
--------------

### Preparing to Install IPF
-------------------------


-   Before installing IPF operators should register their cluster resource in [CiDeR (4)](#CIDER).
    While IPF is capable of publishing information for resources not in CiDeR, ACCESS needs resource
    descriptions in CiDeR to complement the information published with IPF.


-   Identify a single server to run IPF -- a single IPF instance can be used to publish information for multiple resources.


-   To install IPF on a cluster that presents publicly as multiple resources please review this document:
    [Advanced Integration Options](https://www.ideals.illinois.edu/bitstream/handle/2142/99081/XSEDE_SP_Advanced_Integration_Options.pdf)

-   Decide what installation method to use: 
    *     RPM is recommended for production installs, as it is managed by system tools, and creates an "xdinfo" user to run the workflows.
    *     Pip is easier for installs where root access is not available, though some additional environment variables will need to be set.

-   If you already have an older IPF create a backup of the /etc/ipf working configurations:

    $ tar -cf ipf-etc-yyyymmdd.tar /etc/ipf


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



### Software Dependencies


-   Python 3.6 or newer
-   The python-amqp package
-   The python-setuptools package IF installed by RPM.

*These dependencies are encoded in the RPM.*


## Installing IPF
--------------


There are two recommended ways to install IPF: you can use pip install, or you can install from ACCESS RPMs on software.xsede.org.

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


Steps: 1) Configure XSEDE RPM repository trust. For a production version use
    [Production Repo Trust Instructions](https://software.xsede.org/production/repo/repoconfig.txt).
For a development/testing version use
    [Development Repo Trust Instructions](https://software.xsede.org/development/repo/repoconfig.txt).


2)  Install ipf


    $ yum install ipf




## Updating a previous IPF installation
------------------------------------


The JSON files that have been written by previous runs of
ipf_configure would, in some previous versions of IPF get
overwritten by subsequent runs of ipf_configure. This is no
longer the case--previous versions get backed up, not overwritten. They
will *not* be erased by removing OR updating the package (nor will the
service files copied to /etc/init.d be erased).


To perform the update to the latest RPM distribution of ipf:

1.  $ sudo yum update ipf
2.  If there are new workflows you need to configure, follow the
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
IPF using RPM might look like:


/usr/bin/ipf_configure --rpm --resource_name <RESOURCE_NAME> --workflows=extmodules,compute,activity --publish_to_xsede --amqp_certificate /etc/grid-security/cert_for_ipf.pem --amqp_certificate_key /etc/grid-security/key_for_ipf.pem  --modulepath /path/to/modules --scheduler slurm --slurmctl_log <PATH TO slurmctl.log> 


These options mean:


--rpm        IPF was installed using RPM; this lets us know where files should be on disk


--resource_name        The name of your resource.  Not necessary if xdresourceid is in your path
                                   and returns the desired name 
--workflows           Comma delimited list of workflows to configure.  Values can include:
                             compute, activity, extmodules, services
--publish        Necessary if you wish to configure your workflow to publish to ACCESS's
                                      AMQP service for inclusion in Information Services


--amqp_certificate        The path to the certificate to use to authenticate with ACCESS’s AMQP


--amqp_key                  The path to the key for your certificate


--modulepath                The MODULEPATH where the modulefiles for software publishing are 
                                    found.  If not specified $MODULEPATH from the user environment
                                    will be used.


--scheduler                   The batch scheduler in use on your resource.  Typically slurm.


--slurmctl_log               The path (including filename) of your slurmctl log file, used in the 
                                    activity workflow.




Other common options:


--amqp_username          If not using certificates to authenticate, use these to specify 
--amqp_password           username and password


--pip         IPF was installed using “pip install”


For a full list of command line options, please try


$ ipf_configure ----help


-   `ipf_configure` should be run as the user that will run the
    information gathering workflows


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


## Configuring Compute workflow to filter by queue or partition
------------------------------------------------------------


Since IPF 1.5, you have the ability to filter the Compute workflow by 
queue/partition, if you are using SLURM. This is primarily intended for sites
that need to consider GPU nodes as separate resources for the purposes
of computing utilization, etc.


To set parameters of Queues/Partitions for filtering, it is simplest to
manually edit the workflow configuration files.


For example, on can set a params: partitions: inside the compute
workflow in the ExectutionEnvironmentsStep as below:


{ "name": "ipf.glue2.slurm.ExecutionEnvironmentsStep", "params": {
"partitions": "+GPU -RM -LM -XLM -DBMI" } }


This will filter such that only the nodes in the GPU partition are
considered for the Execution Environment. A similar parameter, "queues"
will filter by queue: { "name":
"ipf.glue2.slurm.ExecutionEnvironmentsStep", "params": { "queues":
"+DBMI-GPU -DBMI -RM -RM-shared -RM-small -LM -XLM -GPU -GPU-shared" } }


These parameters can be mixed and matched, and can be applied at other
steps such as ComputingSharesStep and AccelerationEnvironmentsStep.


When filters are applied at the ExecutionEnvironmentsStep, that constrains the
set of nodes considered for total CPU stats (TotalPhysicalCPUs, etc.)


When applied at ComputingSharesStep, it constrains which jobs are counted 
when calculating Used/Available CPUs or Accelerators. 


When applied at the AccelerationEnvironmentsStep, it constrains the set of nodes 
considered for total Accelerator stats.




## Configuring the Batch Scheduler Job Events Workflow
---------------------------------------------------


### Torque


It is necessary for Torque to log at the correct level in order for IPF
to be able to parse the messages that it uses in determining state.
Furthermore, the logging level of Torque can be confusing, as it has
both a log_level and a log_events (which is a bitmask). It is important
to set log_events to 255 to ensure that all types of events are logged.
You can check the setting on your Torque installation by using "qmgr".


### SLURM


The SLURM logs must be in a directory that is local to and accessible to
the IPF installation. `ipf_configure` allows one to set this
location for the workflow.


## Configuring Network Service Files
---------------------------------


Define \<service_name\>.conf files containing these metadata fields about service:
Name, Version, Endpoint, and Capability.


The Name field refers to the GLUE2 Primary protocol name supported by
the service endpoint, as seen in the table below.


Each service can have multiple capabilities, but each line is a
key/value pair, so to publish multiple capabilities for a service, have
a line that starts "Capability =" for each value. (see example below).
The Capability field describe what services the endpoint URL
supports.


Valid Capability values are listed in the table below. Please edit your
service.conf files to include appropriate Capability values.


A key/value pair for SupportStatus in your service.conf file will override the default,
which is the support status of your service as published in CiDeR.


Globus Connect Server (GCS) services should not be registered as network services.
ACCESS discovers these automatically from Globus.


------------------------------------------------------------------------


A table of valid Name, Version and Capability values:


    Name                Version        Capability
    org.globus.openssh  5.y.z          login.remoteshell
                                       login.remoteshell.gsi


Sample Service publishing file:
    #%Service1.0###################################################################
    ##
    ## serviceinfofiles/org.openssh-x.y.z.conf
    ##


    Name = org.openssh
    Version = 8.x
    Endpoint = delta.ncsa.access-ci.org 
    Capability = login.shell.local-password-mfa
    Capability = login.shell.pubkey
    SupportStatus = production


## Software Module Publishing Best Practices
-----------------------------------------


The IPF Software Module workflow publishes information about locally
installed software available through modules or Lmod. IPF tries to make
intelligent inferences from the system installed modules files when it
publishes software information. There are some easy ways, however, to
add information to your module files that will enhance/override the
information otherwise published.


The Modules workflows traverses your MODULEPATH and infers fields such
as Name and Version from the directory structure/naming conventions of
the module file layout. Depending on the exact workflow steps, fields
such as Description may be blank, or inferred from the stdout/stderr
text of the module. However, the following fields can always be
explicitly added to a module file:


    Description:
    URL:
    Category:
    Keywords:
    SupportStatus:
    SupportContact:


Each field is a key: value pair. The IPF workflows are searching the
whole text of each module file for these fields. They may be placed in a
module-whatis line, or in a comment, and IPF will still read them.


The URL field should point to local user documentation.


The Category field may contain one or more comma separated fields of
science or software categories. ACCESS's official fields of science are
listed at `https://operations-api.access-ci.org/wh2/api/schema/swagger-ui/`.
Some recommended software categories are: data, compiler, language,
debugger, profiler, optimization, system, utilities. Category values are
discoverable in the Research Software Portal in the software *Topics*
field.


The Keywords field may contain any other desired keywords.


The SupportStatus field should be: development, testing, or production.


The SupportContact field must contain either: * the exact URL:
`https://info.xsede.org/wh1/xcsr-db/v1/supportcontacts/globalid/helpdesk.xsede.org/`


-   another URL that returns a JSON document formatted exactly like the one shown above (but with different values)


-   or a one-liner JSON blob of the form:
    `[{"GlobalID":"support.access-ci.org","Name":"ACCESS Support","Description":"ACCESS Support","ShortName":"ACCESS","ContactURL":"https://support.access-ci.org"}]`


All XSEDE registered support contact organizations are found at:
`https://info.xsede.org/wh1/xcsr-db/v1/supportcontacts/`
To register a new support contact submit a ticket to ACCESS Operations with the
Subject: Please register a new Support Contact Organization.


`ipf_configure` offers the opportunity to define a default SupportContact that is published for every module
that does not define its own. By default, this value is:
`https://info.xsede.org/wh1/xcsr-db/v1/supportcontacts/globalid/helpdesk.xsede.org/`


Example:


    #%Module1.0#####################################################################
    ##
    ## modulefiles/accessusage/1.5.2
    ##
    module-whatis "Description: ACCESS Allocation Usage lookup tool"
    module-whatis "URL: http://software.xsede.org/production/accessusage/latest/"
    module-whatis "Category: System tools"
    module-whatis "Keywords: information"
    module-whatis "SupportStatus: testing"
    module-whatis "SupportContact: https://info.xsede.org/wh1/xcsr-db/v1/supportcontacts/globalid/support.access-ci.org/"


However, IPF would read these just as well if they were:


    #%Module1.0#####################################################################
    ##
    ## modulefiles/accessusage/1.5.2
    ##
    #module-whatis "Description: Allocation Usage lookup tool"
    # "URL: http://software.xsede.org/production/accessusage/latest/"
    # Random text that is irrelevant "Category: System tools"
    # module-whatis "Keywords: information"
    module-whatis "SupportStatus: testing"
    module-whatis "SupportContact: https://info.xsede.org/wh1/xcsr-db/v1/supportcontacts/globalid/support.access-ci.org/"


With this in mind, it is recommended that you add these fields to relevant module files.
The decision on whether to include them as module-whatis lines (and therefore visible as
such to local users) or to include them as comments is up to each operator.


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


2)  To test the compute workflow, execute:


    # service ipf-RESOURCE_NAME-glue2-compute start


This init script starts a workflow that periodically gathers (every
minute by default) and publishes information about your compute
resource. This workflow generates two types of documents. The first type
describes the current state of your resource. This document doesn't
contain sensitive information and ACCESS makes it available without
authentication. The second type describes the queue state of your
resource, contains sensitive information (user names), and will only be
made available to authenticated ACCESS users.


The log file is in /var/ipf/RESOURCE_NAME_compute.log (or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_compute.log) and should
contain messages resembling:


    2013-05-30 15:50:43,590 - ipf.engine - INFO - starting workflow sge_compute
    2013-05-30 15:50:45,403 - ipf.publish.AmqpStep - INFO - step-12 - publishing representation PrivateOgfJson of Private expanse.sdsc.access-ci.org
    2013-05-30 15:50:45,626 - ipf.publish.FileStep - INFO - step-14 - writing representation PrivateOgfJson of Private expanse.sdsc.access-ci.org
    2013-05-30 15:50:45,878 - ipf.publish.AmqpStep - INFO - step-11 - publishing representation PublicOgfJson of Public expanse.sdsc.access-ci.org
    2013-05-30 15:50:46,110 - ipf.publish.FileStep - INFO - step-13 - writing representation PublicOgfJson of Public expanse.sdsc.access-ci.org
    2013-05-30 15:50:46,516 - ipf.engine - INFO - workflow succeeded


Typical failures are caused by the execution environment not having
specific commands available. Review the environment setup in the init
script.


You can examine /var/ipf/RESOURCE_NAME_compute.json (or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_compute.json) to determine if
the description of your resource is accurate. You can also exampine
/var/ipf/RESOURCE_NAME_activities.json ( or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_activities.json) to determine
if the description of the jobs being managed by your resource is
correct.


3)  To test the activity workflow, execute:


    # service ipf-RESOURCE_NAME-glue2-activity start


This init script starts a long-running workflow that watches your
scheduler log files and publishes information about jobs as they are
submitted and change state.


The log file is in /var/ipf/RESOURCE_NAME_activity.log (or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_activity.log) and should
contain messages resembling:


    2013-05-30 16:04:26,030 - ipf.engine - INFO - starting workflow pbs_activity
    2013-05-30 16:04:26,038 - glue2.pbs.ComputingActivityUpdateStep - INFO - step-3 - running
    2013-05-30 16:04:26,038 - glue2.log - INFO - opening file 27-6930448 (/opt/pbs6.2/default/common/reporting)
    2013-05-30 16:05:50,067 - glue2.log - INFO - reopening file 27-6930448 (/opt/pbs6.2/default/common/reporting)
    2013-05-30 16:05:50,089 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226387.user.resource.access-ci.org
    2013-05-30 16:05:50,493 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226814.user.resource.access-ci.org
    2013-05-30 16:06:12,109 - glue2.log - INFO - reopening file 27-6930448 (/opt/pbs6.2/default/common/reporting)
    2013-05-30 16:06:12,361 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226867.user.resource.access-ci.org
    2013-05-30 16:06:12,380 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226868.user.resource.access-ci.org
    2013-05-30 16:06:12,407 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226788.user.resource.access-ci.org
    2013-05-30 16:06:12,428 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226865.user.resource.access-ci.org
    2013-05-30 16:06:12,448 - ipf.publish.AmqpStep - INFO - step-4 - publishing representation ComputingActivityOgfJson of ComputingActivity 1226862.user.resource.access-ci.org
    ...


You can look at the activity information published in
/var/ipf/RESOURCE_NAME_activity.json (or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_activity.json). This file
contains the sequence of activity JSON documents published.


4)  To test the Network Service (services) workflow, execute:


    # service ipf-RESOURCE_NAME-glue2-services start


This init script starts a workflow that periodically gathers (every hour
by default) and publishes service information from the service
definition files.


The log file is in /var/ipf/RESOURCE_NAME_services.log (or
$INSTALL_DIR/ipf/var/ipf/RESOURCE_NAME_services.log) and should
contain messages resembling:


    2013-05-30 15:27:05,309 - ipf.engine - INFO - starting workflow s
    2013-05-30 15:27:05,475 - ipf.publish.AmqpStep - INFO - step-3 - publishing representation ASOgfJson of AbstractServices expanse.sdsc.access-ci.org
    2013-05-30 15:27:05,566 - ipf.publish.FileStep - INFO - step-4 - writing representation ASOgfJson of AbstractServices expanse.sdsc.access-ci.org
    2013-05-30 15:27:06,336 - ipf.engine - INFO - workflow succeeded


If any of the steps fail, that will be reported and an error message and
stack trace should appear. Typical failures are caused by the
environment not having specific variables or commands available.


This workflow describes your modules as a JSON document containing GLUE
v2.0 Application Environment and Application Handle objects. This
document is published to the ACCESS RabbitMQ services in step-3 and is
written to a local file in step-4. You can examine this local file in
/var/ipf/RESOURCE_NAME_apps.json. If you see any errors in gathering
module information, please submit an ACCESS ticket.


## Log File Management
-------------------


The log files described above will grow over time. The logs are only
needed for debugging, so they can be deleted whenever you wish.
logrotate is a convenient tool for creating archival log files and
limiting the amount of files kept. One note is that the ipf workflows
keep the log files open while they run, so you should either use the
copytruncate option or have a post-rotate statement to restart the
corresponding ipf service.


## References
==========


- <a name="IPF">(1) IPF is open source and maintained at
    [https://github.com/access-ci-org/ipf](https://github.com/access-ci-org/ipf).</a>
- <a name="infoserv">(2) [ACCESS Information Sharing Platform](https://operations-api.access-ci.org/).</a>
- <a name="CiDeR">(4) [CyberInfrastructure Description Repository "CiDeR"](https://cider.access-ci.org/).</a>
- <a name="glue2">(5) [GLUE2 Standard Format](https://www.ogf.org/documents/GFD.147.pdf).</a>


## Appendix: Configuration File Background
=======================================


There are several files associated with IPF, both pre and post
configuration that help determine how workflows are configured and how
and when they run.


### Pre-configuration templates
---------------------------


Depending on how you installed IPF, the IPF source tree can be found in
various locations.
If you used RPM to install, the source code can be found at
/usr/lib/python3.6/site-packages/ipf/. 
Note, however, that the $IPF_ETC_PATH dir for an RPM install is /etc/ipf 
(that is to say, inside the canonical /etc directory) 

If you used pip to install, the source
code can be found in your python's site_packages/ipf/ directory. 
To find the site_packages directory for your python, you can run: 


     $python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'

The pip-installed IPF_ETC_PATH path is this directory above, with /etc/ipf/
added to the end, e.g. /usr/lib/python3.6/site-packages/etc/ipf


If you used a tarball or git checkout, you should be able to find the
source code on your filesystem yourself.


IPF ships with pre-configuration workflow templates for the various
schedulers. They can be found in the IPF_ETC_PATH directory in the
$IPF_ETC_PATH/workflow/templates directory. The template files as currently
constructed are: generic_publish.json generic_print.json
glue2/lmod.json glue2/serviceremotepublish.json
glue2/moab_pbs_compute.json glue2/extmodules.json
glue2/extmodulesremote.json glue2/condor_compute.json
glue2/abstractservice.json glue2/pbs_activity.json
glue2/sge_activity.json glue2/ipfinfo_publish.json
glue2/sge_compute.json glue2/pbs_compute.json
glue2/slurm_activity.json glue2/modules.json glue2/slurm_compute.json
glue2/openstack_compute.json glue2/catalina_pbs_compute.json


These workflow templates are automatically used in workflow
configuration via the ipf_configure script.


### Post-configuration workflow files
---------------------------------


After you configure your workflows, the configured workflows will be
represented by json files in $IPF_ETC_PATH/workflow and/or
$IPF_ETC_PATH/workflow/glue2. There will be a json file for each configured
workflow, and various workflows will have a second "periodic" workflow
that calls the other at a configurable delay. These workflow files can
be invoked by $INSTALL_DIR/ipf-VERSION/ipf/bin/ipf_workflow
\<workflow.json\> However, in production, they are more commonly invoked
by init scripts described below.


### Workflow init scripts
---------------------


The ipf_configure script generates an init script for each
workflow you configure, and puts them in $IPF_ETC_PATH/init.d/ Each script
runs one workflow, on a periodic basis (using the periodic workflows
described above). It is important to note that the scripts in
$IPF_ETC_PATH/init.d are NOT automatically configured to be run by the
operating system: this must be done manually, typically by being copied
into the system /etc/init.d directory as part of the installation and
configuration process documented in this file. Thus, to see what is
actually being used to invoke the workflows in production, one must find
the operating system location of init scripts, and see what is
configured there.
