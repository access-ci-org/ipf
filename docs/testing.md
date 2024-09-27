# access-ci-org/ipf %VER%-%REL%
=====================


# Testing


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

