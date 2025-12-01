###############################################################################
#   Copyright 2015 The University of Texas at Austin                          #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
###############################################################################

# TODO - get amqp username / password from .netrc

import argparse
import copy
import getpass
import json
import os
import pathlib
import pprint
import socket
import subprocess
import sysconfig
import textwrap
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from ipf.paths import IPF_ETC_PATH, IPF_VAR_PATH

# module level data
resources = {}

### Getter Functions
def get_args( params=None ):
    key = 'args'
    try:
        args = resources[key]
    except KeyError:
        args = parseargs()
        resources[key] = args
    return args


def get_short_resource_name():
    key = 'short_resource_name'
    try:
        val = resources[key]
    except KeyError:
        val = get_args().resource_name.split(".")[0]
        resources[key] = val
    return val


def get_modules():
    key = 'modules'
    try:
        val = resources[key]
    except KeyError:
        try:
            args = get_args()
            parts = args.modules.split(",")
        except AttributeError:
            val = ""
        else:
            init_file = pathlib.Path( os.environ['MODULESHOME'], 'init', 'bash' )
            strings = [ f"source {init_file}" ]
            strings.extend(
                f"module load {module_name}" 
                for module_name in parts
            )
            val = "\n".join( strings )
        resources[key] = val
    return val

def get_environment_variables():
    key = "environment_variables"
    try:
        val = resources[key]
    except KeyError:
        args = get_args()
        data = {}
        strings = []
        if args.environment:
            for _envvar in args.environment.split(","):
                # ( name, value ) = _envvar.split("=")
                # data[name] = value
                strings.append( f"export {_envvar}" )
        val = "\n".join( strings )
        resources[key] = val
    return val


def getWorkflowDir():
    return pathlib.Path( IPF_ETC_PATH, "workflow" )

def getWorkflowGlueDir():
    return getWorkflowDir() / "glue2"

def getWorkflowTemplateGlueDir():
    return getWorkflowDir() / "templates" / "glue2"


def get_workflow_template():
    args = get_args()
    prefix = ""
    # 20260212(aloftus) - remove support for "activity" workflow
    # if args.workflow in [ 'compute', 'activity' ]:
    if args.workflow == 'compute' :
        # scheduler is part of filename for compute and activity workflows
        prefix = f"{args.scheduler}_"
    filename = f"{prefix}{args.workflow}.json"
    path = getWorkflowTemplateGlueDir() / filename
    return read_json_file( path )


### Helper functions

def read_json_file( path: pathlib.Path ) -> dict:
    with path.open() as fh:
        return json.load( fh )


def write_json_file( path: pathlib.Path, data: dict ) -> None:
    # path = pathlib.Path( filename )
    mk_file_backup( path )
    with path.open( mode='w' ) as fh:
        json.dump( data, fh, indent=4, sort_keys=True )


def mk_file_backup( path: pathlib.Path ) -> None:
    if path.exists():
        ts = time.strftime( '%Y-%m-%d-%X', time.localtime() )
        tgt = f"{path}.backup-{ts}"
        # TODO - logging.debug
        print( f"  backing up '{path}' as '{tgt}'" )
        path.rename( tgt )


def get_workflow_steps_by_name( workflow: dict, step_name: str ) -> list:
    step_data = []
    for step in workflow["steps"]:
        if step["name"] == step_name:
            step_data.append( step )
    if len( step_data ) < 1:
        raise UserWarning( f"Didn't find any steps with name, '{step_name}'" )
    return step_data


def set_step_parameter(
        workflow,
        step_name,
        parameter_name,
        parameter_value,
        missing_ok=False,
    ):
    ''' Singular version of set_step_parameters,
        for readability when setting only one parameter
    '''
    params = { parameter_name: parameter_value }
    set_step_parameters( workflow, step_name, params, missing_ok )


def set_step_parameters(
        workflow: dict,
        step_name: str,
        params: dict,
        missing_ok=False,
    ) -> None:
    ''' In workflow["steps"]["name"] == step_name
        for each key,value pair in params:
        set ["parameters"][key] = value
        If step_name isn't found throw an error unless missing_ok is True
    '''
    # pprint.pp( { "WORKFLOW": workflow } )
    try:
        # In general, expect only 1 matching workflow step name,
        # even though get_workflow_steps_by_name returns a list,
        # just grab the first one
        step_data = get_workflow_steps_by_name( workflow, step_name )[0]
    except UserWarning as e:
        if not missing_ok:
            raise e
    # pprint.pp( { "STEP DATA": step_data } )
    for parameter_name,value in params.items():
        step_data["params"][parameter_name] = value


# Parseargs does all the requirement processing,
# ensuring all the necessary pieces of a workflow are provided,
# thus simplifying the workflow creation/manipulation functions
# by putting most error checking here

def parseargs():
    # Parse arguments
    constructor_args = {
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": "Configure an ACCESS  reporting workflow.",
        }
    parser = argparse.ArgumentParser( **constructor_args )

    # Required, always
    parser.add_argument(
        '--resource_name',
        required=True,
        help='Set the resource name. (Required)'
    )
    parser.add_argument(
        '--workflow',
        required=True,
        choices=['extmodules', 'compute' ], #20260212(aloftus) - removed "activity"
        help='Workflow to configure (Required)'
    )

    # Publishing to AMQP
    publish_group = parser.add_argument_group(
        title="Publish Authentication",
        description=textwrap.dedent( """
            If --publish is present, must also provide an authentication combo.
            One combo of user/pass or cert/key is required alongside --publish.
            """
        ),
    )
    publish_group.add_argument(
        '--publish',
        action='store_true',
        help='Configure the services to publish to AMQP'
    )
    user_group = publish_group.add_mutually_exclusive_group()
    pwd_group = publish_group.add_mutually_exclusive_group()
    # about to interleave user_group and pwd_group assignments
    # so that the help message puts username/password together
    # and then cert/key also display together in the help message
    user_group.add_argument(
        '--amqp_username',
        help='Username for publishing to AMQP.'
    )
    pwd_group.add_argument( #note pwd_group
        '--amqp_password',
        help='Password for publishing to AMQP.'
    )
    user_group.add_argument( #note this is user_group again
        '--amqp_certfile',
        help='Path to certificate file for publishing to AMQP.'
    )
    pwd_group.add_argument( #finally, one more pwd_group
        '--amqp_keyfile',
        help='Path to certificate key file for publishing to AMQP.'
    )

    # Optional, used in init.d scripts
    init_group = parser.add_argument_group(
        title="Init.d Script Generation",
        description="Settings and variables for init scripts",
    )
    init_group.add_argument(
        '--modules',
        help=textwrap.dedent( '''
            Any modules to be loaded in the init scripts.
            Format is comma-separated list of values.
            '''
        )
    )
    init_group.add_argument(
        '--environment',
        help=textwrap.dedent( '''
            Environment variables to be loaded in the init scripts, such as
            "MODULEPATH" or "SERVICEPATH" or
            "batch scheduler commands that need to be in PATH" or
            "scheduler-related environment variables may need to be set".
            Format is a comma separated list of VARNAME=VALUE pairs.
            '''
        )
    )

    # required by compute workflow
    compute_group = parser.add_argument_group(
            title="Compute Workflow Settings",
            description="Required when configuring compute workflow",
            )
    compute_group.add_argument('--organization_name')
    compute_group.add_argument('--city')
    compute_group.add_argument('--country')
    compute_group.add_argument('--latitude')
    compute_group.add_argument('--longitude')
    compute_group.add_argument(
        '--compute_interval',
        default=60,
        help='Wait COMPUTE_INTERVAL seconds before re-running the compute workflow'
    )

    # required for compute and activity
    scheduler_group = parser.add_argument_group(
        title="Scheduler",
        description=textwrap.dedent( """
            Scheduler is required for compute workflow.
            Scheduler_params is optional.
            """
        ),
    )
    # note: if scheduler choices change, make sure to also adjust scheduler vetting
    scheduler_group.add_argument(
        '--scheduler',
        choices=['pbs', 'slurm' ], #20260202(aloftus) - removed "sge"
        help='set the scheduler name'
    )
    # optional for compute and activity
    scheduler_group.add_argument(
        '--scheduler_params',
        action='store',
        help='comma delimited key:value pairs for parameters for your scheduler'
    )

    # 20260212(aloftus) - remove support for "activity" workflow
    # required for activity workflow
    # activity_group = parser.add_argument_group(
    #         title="Activity Workflow",
    #         description="Scheduler logs are required for activity workflow",
    #         )
    # activity_choices = activity_group.add_mutually_exclusive_group()
    # activity_choices.add_argument(
    #     '--slurmctl_log',
    #     help='The full path (including filename) for your slurmctl.log file'
    # )
    # activity_choices.add_argument(
    #     '--pbs_log_dir',
    #     help='The full path to PBS log dir'
    # )
    # 20260202(aloftus) - remove sge support
    #                   - scheduler is no longer used and
    #                   - IPF support for sge is very likely broken
    # activity_choices.add_argument(
    #     '--sge_reporting_log',
    #     help='The full path (including filename) for your SGE reporting log'
    # )


    # Optional for extmodules workflow
    extmodules_group = parser.add_argument_group(
        title="Extmodules Workflow",
        description="Options for configuring an extmodules workflow.",
        )
    extmodules_group.add_argument(
        '--support_contact',
        help='The support contact URL to be published in your ExtModules workflow'
    )
    extmodules_group.add_argument(
        '--modules_interval',
        default=24,
        help='Wait MODULES_INTERVAL hours before re-running the ExtModules workflow'
    )
    extmodules_group.add_argument(
        '--lmod_cache_file',
        help='full path to lmod cache file to use in ExtModules workflow'
    )
    extmodules_group.add_argument(
        '--modules_exclude',
        help='comma delimited list of module names to exclude.'
    )
    extmodules_group.add_argument(
        '--modules_recurse',
        action='store_true',
        help=textwrap.dedent( '''
            legacy: assume that module_path dirs and their recursive subdirs
            contain at most one level of semantically important subdirs
            '''
        ).strip("\n"),
    )
    extmodules_group.add_argument(
        '--ignore_toplevel_modulefiles',
        action='store_true',
        help=textwrap.dedent( '''
            legacy behavior: assume that modulefiles at the top level
            of each module_path directory should not be reported as software.
            '''
        ).strip("\n"),
    )

    args = parser.parse_args()

    # 20260212(aloftus) - remove support for "activity" workflow
    # Vet scheduler (required for compute and activity workflows)
    # if args.workflow in [ 'compute', 'activity' ]:
    #     if not args.scheduler:
    #         msg = "--scheduler is required for compute and activity workflows."
    #         raise SystemExit( msg )

    # Vet compute workflow requirements
    if args.workflow == "compute":
        required_args = [
            "scheduler",
            "organization_name",
            "city",
            "country",
            "latitude",
            "longitude",
            "compute_interval",
            ] 
        if not all( [ getattr( args, x ) for x in required_args ] ):
            msg = textwrap.dedent( f"""
                Missing one or more of {required_args}.
                All must be present for configuring compute workflow.
            """ )
            raise SystemExit( msg )

    # 20260212(aloftus) - remove support for "activity" workflow
    # Vet activity workflow requirements
    # if args.workflow == "activity":
    #     msg = None
    #     if args.scheduler == "slurm":
    #         if not args.slurmctl_log:
    #             msg = textwrap.dedent( """
    #                 --slurmctl_log required when scheduler=slurm and workflow=activity
    #                 """ ).strip("\n")
    #         else:
    #             sctl_logfile = pathlib.Path( args.slurmctl_log )
    #             if not sctl_logfile.is_file():
    #                 msg = f"Cannot access slurmctl log '{sctl_logfile}'"
    #     elif args.scheduler == "pbs":
    #         if not args.pbs_log_dir:
    #             msg = textwrap.dedent( """
    #                 --slurmctl_log required when scheduler=pbs and workflow=activity
    #                 """ ).strip("\n")
    #         else:
    #             pbs_logdir = pathlib.Path( args.pbs_log_dir )
    #             if not pbs_logdir.is_dir():
    #                 msg = f"Cannot access pbs log dir '{pbs_logdir}"
    #     # 20260202(aloftus) - remove sge support
    #     # elif args.scheduler == "sge" and not args.sge_reporting_log:
    #     #     msg = textwrap.dedent( """
    #     #         --slurmctl_log required when scheduler=slurm and workflow=activity
    #     #         """ ).strip("\n")
    #     if msg:
    #         raise SystemExit( msg )

    # Ensure amqp credentials if publish was requested
    if args.publish:
        # verify auth combo makes sense (username/password OR cert/key)
        msg = None
        if args.amqp_username:
            if not args.amqp_password:
                msg = "--amqp_password is required alongside --amqp_username"
        else:
            # certfile was specified, validate existence
            certfile = pathlib.Path( args.amqp_certfile )
            if not certfile.is_file():
                msg = f"cannot access --amqp_certfile '{certfile}'"
            keyfile = pathlib.Path( args.amqp_keyfile )
            if not args.amqp_keyfile:
                msg = "--amqp_keyfile is required alongside --amqp_certfile"
            elif not keyfile.is_file():
                msg = f"cannot access --amqp_keyfile '{keyfile}'"
        if msg:
            raise SystemExit( msg )

    return args


### Main workflow manipulation functions


def set_resource_name( workflow ):
    args = get_args()
    res_name = get_short_resource_name()
    workflow["name"] = f"{res_name}_{workflow['name']}"
    set_step_parameter(
        workflow = workflow,
        step_name = "ipf.sysinfo.ResourceNameStep",
        parameter_name = "resource_name",
        parameter_value = args.resource_name,
    )


def set_extmodules_params( workflow: dict ) -> None:
    args = get_args()
    step_name = "ipf.glue2.modules.ExtendedModApplicationsStep"
    argname2paramname_map = {
        "modules_exclude": "exclude",
        "ignore_toplevel_modulefiles": "ignore_toplevel_modulefiles",
        "lmod_cache_file": "lmod_cache_file",
        "modules_recurse": "modules_recurse",
        "support_contact": "default_support_contact",
    }
    params = {}
    for argname,paramname in argname2paramname_map.items():
        user_provided_value = getattr( args, argname )
        if user_provided_value:
            params[ paramname ] = user_provided_value
    set_step_parameters( workflow, step_name, params )


def set_location( workflow: dict ) -> None:
    args = get_args()
    step_name = "ipf.glue2.location.LocationStep"
    argname2paramname_map = {
        "organization_name": "Name",
        "city": "Place",
        "country": "Country",
        "latitude": "Latitude",
        "longitude": "Longitude",
    }
    location_params = {}
    for argname,paramname in argname2paramname_map.items():
        user_provided_value = getattr( args, argname )
        if user_provided_value:
            location_params[ paramname ] = user_provided_value
    params = { "location": location_params }
    set_step_parameters( workflow, step_name, params )


def update_filepublish_paths( workflow ):
    res_name = get_short_resource_name()
    step_name = "ipf.publish.FileStep"
    step_matches = get_workflow_steps_by_name( workflow, step_name )
    for step in step_matches:
        old_name = step["params"]["path"]
        new_name = f"{res_name}_{old_name}"
        step["params"]["path"] = new_name


def add_amqp_publish_step( workflow ):
    args = get_args()
    if not args.publish:
        return False
    workflow_name = args.workflow
    if workflow_name == "compute":
        publish_step = "ipf.glue2.compute.PublicOgfJson"
        exchange = "glue2.compute"
        description = "Publish compute resource description to ACCESS-CI"
    elif workflow_name == "extmodules":
        publish_step = "ipf.glue2.application.ApplicationsOgfJson"
        exchange = "glue2.applications"
        description = "Publish modules to ACCESS-CI"

    # 20260212(aloftus) - remove support for "activity" workflow
    # elif workflow_name == "activity":
    #     publish_step = "ipf.glue2.computing_activity.ComputingActivityOgfJson"
    #     exchange = "glue2.computing_activity"
    #     description = "Publish job updates to ACCESS-CI"

    amqp_step = {
        "name": "ipf.publish.AmqpStep",
        "description": description,
        "params": {
            "publish": [ publish_step ],
            "services": [
                "opspub.access-ci.org",
                "opspub-alt.access-ci.org",
            ],
            "vhost": "infopub",
            "exchange": exchange,
            "ssl_options": {
                "ca_certs": "ca-certificates/ca_certs.pem",
                # this is where certfile & keyfile get added
                # "certfile": path to certfile,
                # "keyfile": path to certificate keyfile,
            },
            # this is where username & password get added
            # "username": username for AMQP login
            # "password": password for username for AMQP login
        },
    }
    # add in the auth options
    if args.amqp_username:
        amqp_step["params"]["username"] = args.amqp_username
        amqp_step["params"]["password"] = args.amqp_password
    else:
        amqp_step["params"]["ssl_options"]["certfile"] = args.amqp_certfile
        amqp_step["params"]["ssl_options"]["keyfile"] = args.amqp_keyfile
    workflow["steps"].append(amqp_step)
    if workflow_name == "compute":
        # this is how the "compute" workflow also publishes activity data
        amqp_step = copy.deepcopy(amqp_step)
        amqp_step["description"] = "Publish description of current jobs to ACCESS-CI"
        amqp_step["params"]["publish"] = ["ipf.glue2.compute.PrivateOgfJson"]
        amqp_step["params"]["exchange"] = "glue2.computing_activities"
        workflow["steps"].append(amqp_step)


# 20260212(aloftus) - remove support for "activity" workflow
# def update_activity_logfile( workflow: dict ) -> None:
#     args = get_args()
#     res_name = get_short_resource_name()
#     step_name = f"ipf.glue2.{args.scheduler}.ComputingActivityUpdateStep"
#     params_to_update = {
#         "position_file": f"{res_name}_activity.pos",
#     }
#     if args.scheduler == "slurm":
#         params_to_udpate["slurmctl_log_file"] = args.slurmctl_log
#     elif args.scheduler == "pbs":
#         params_to_udpate["server_logs_dir"] = args.pbs_log_dir
#     set_step_parameters( workflow, step_name, params_to_update )


def write_workflow_file( workflow: dict ) -> None:
    args = get_args()
    res_name = get_short_resource_name()
    path = getWorkflowGlueDir() / f'{res_name}_{args.workflow}.json'
    print( f"  -> writing workflow to {path}" ) #INFO
    write_json_file( path, workflow )


def write_periodic_workflow_file( max_interval ):
    args = get_args()
    res_name = get_short_resource_name()
    step_name = f"{res_name}_{args.workflow}_periodic"
    periodic_json = {
        "name" : step_name,
        "description" : f"Gather GLUE2 {args.workflow} information periodically",
        "steps" : [
            {
                "name": "ipf.step.WorkflowStep",
                "params": {
                    "workflow" : f"glue2/{res_name}_{args.workflow}.json",
                    "maximum_interval" : max_interval,
                },
            },
        ],
    }
    path = getWorkflowGlueDir() / f"{step_name}.json"
    print( f"  -> writing extmodules periodic workflow to '{path}'" )
    write_json_file( path, periodic_json )

### Main functions


def make_workflow():
    args = get_args()
    workflow_data = get_workflow_template()
    set_resource_name( workflow_data )
    update_filepublish_paths( workflow_data )
    add_amqp_publish_step( workflow_data )
    # pprint.pp( { "DEBUG - WORKFLOW after add_amqp_publish_step": workflow_data } )
    # do unique per-workflow parts
    if args.workflow == "extmodules":
        # do any extmodules specific configuration
        set_extmodules_params( workflow_data )
    elif args.workflow == "compute":
        # do any compute specific configuration
        set_location( workflow_data )

    # 20260212(aloftus) - remove support for "activity" workflow
    # elif args.workflow == "activity":
    #     # do any activity specific configuration
    #     update_activity_logfile( workflow_data )

    # write the workflow to file
    # pprint.pprint( workflow_data ) #DEBUG
    write_workflow_file( workflow_data )


def make_periodic_workflow():
    args = get_args()
    max_interval = None
    if args.workflow == "compute":
        max_interval = int( args.compute_interval )
    elif args.workflow == "extmodules":
        max_interval = int( args.modules_interval ) * 60 * 60
    if max_interval:
        write_periodic_workflow_file( max_interval )


def make_init():
    args = get_args()
    res_name = get_short_resource_name()
    modules_to_load = get_modules()
    env_vars = get_environment_variables()
    init_file = pathlib.Path(
        IPF_ETC_PATH,
        'init.d',
        f'ipf-{res_name}-glue2-{args.workflow}'
    )
    mk_file_backup( init_file )
    template_file = pathlib.Path( IPF_ETC_PATH, 'init.d', 'init.template' )
    pattern = "___DATA_FROM_CONFIGURE.PY_HERE___"
    pattern_was_found_already = False
    with template_file.open() as infile, init_file.open('w') as outfile:
        for line in infile:
            if pattern_was_found_already:
                outfile.write(line)
            else:
                if pattern in line:
                    # Dump out the config
                    outfile.write(
                        textwrap.dedent( f"""
                            export IPF_ETC_PATH={IPF_ETC_PATH}
                            export IPF_VAR_PATH={IPF_VAR_PATH}
                            {env_vars}
                            WORKFLOW_NAME={res_name}_{args.workflow}_periodic
                            WORKFLOW_DIR={getWorkflowDir()}
                            INIT_FILE={init_file}
                            RES_NAME={res_name}
                            {modules_to_load}
                            """
                        )
                    )
                    pattern_was_found_already = True
                else:
                    outfile.write(line)


if __name__ == "__main__":
    make_workflow()
    make_periodic_workflow()
    make_init()
