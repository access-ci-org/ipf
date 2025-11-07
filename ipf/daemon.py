
###############################################################################
#   Copyright 2012-2014 The University of Texas at Austin                     #
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

import logging
import os
import sys
import time
import pathlib

from ipf.paths import IPF_VAR_PATH

logger = logging.getLogger(__name__)

##############################################################################################################

class OneProcessOnly:
    def __init__(self, pidfile):
        if ( pidfile is None or len(pidfile) < 1 ):
            raise UserWarning( 'pidfile cannot be empty' )
        self.pidfile = pathlib.Path( pidfile )
        self.hostname = os.uname().nodename

    def start(self):
        if self._isRunning():
            logger.error(f"process already running at {self.pidfile}")
            return
        self._writePid()
        self.run()
        self._removePid()

    def _isRunning(self):
        # already validated pidfile in __init__
        # if self.pid_file_name is None:
        #     # no way to tell
        #     False
        retval = False
        if self.pidfile.exists():
            pid_val, pid_host = self.pidfile.read_text().splitlines()[:2]
            # with self.pid_file_name.open() as pid_file:
            #     pid_str = pid_file.readline().strip()
            #     pid_host = pid_file.readline().strip()
            # logger.debug(f"pid is {pid_val} on host {pid_host}")
            # check validity of pid_host
            if ( pid_host is None or len(pid_host) < 1 ):
                raise UserWarning( f'Missing hostname in pid file {self.pidfile}' )
            # check validity of pid_val
            if ( pid_val is None or len(str(pid_val)) < 1 ):
                raise UserWarning( f'Missing hostname in pid file {self.pidfile}' )
            # check for host match
            if ( pid_host != self.hostname ):
                logger.debug( f'started on {pid_host}' )
                retval = True
            # process is local, check if running
            # elif (pid_val is not None) and os.path.exists(f"/proc/{pid_val}"):
            elif ( pathlib.Path( '/proc', pid_val ).exists() ):
                # could check /proc/pid_str/cmdline and ...
                logger.debug("found running daemon")
                retval = True
        else:
            # logger.debug("pid file not found")
            retval = False
        return retval

    def _writePid(self):
        # already validated pidfile in __init__
        # if self.pid_file_name is None:
        #     return
        # save process id in the .pid file
        # pid_file = open(self.pid_file_name,"w")
        # pid_file.write(str(os.getpid()))
        # pid_file.write(str(self.hostname))
        # pid_file.close()
        self.pidfile.write_text( f'{os.getpid()}\n{self.hostname}' )

    def _removePid(self):
        # already validated pidfile in __init__
        # if self.pid_file_name is None:
        #     return
        # try:
        #     os.remove(self.pid_file_name)
        # except IOError:
        #     logger.warning("failed to remove pid file %s" % self.pidfile)
        self.pidfile.unlink( missing_ok=True )

    def _redirect(self, stdin_file_name, stdout_file_name, stderr_file_name):
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(stdin_file_name, 'r')
        so = open(stdout_file_name, 'a+')
        se = open(stderr_file_name, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def run(self):
        raise NotImplementedError()

##############################################################################################################

class OneProcessWithRedirect(OneProcessOnly):
    def __init__(self, pidfile=None, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
        super().__init__(pidfile)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def start(self):
        if self._isRunning():
            logger.error(f"process already running at {self.pidfile}")
            return
        self._writePid()
        self._redirect(self.stdin,self.stdout,self.stderr)
        self.run()
        self._removePid()
 
    def run(self):
        raise NotImplementedError()

##############################################################################################################

class Daemon(OneProcessOnly):
    def __init__(self, pidfile=None, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
        super().__init__(pidfile)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def start(self):
        if not self._isRunning():
            self._daemonize()
            self._writePid()
            self.run()

    def _daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            logger.error( f"fork #1 failed: {e.errno} {e.strerror}\n" )
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            logger.error( f"fork #2 failed: {e.errno} {e.strerror}\n" )
            sys.exit(1)

        self._redirect(self.stdin,self.stdout,self.stderr)
 
    def run(self):
        raise NotImplementedError()

##############################################################################################################

class TestDaemon(Daemon):
    def __init__(self):
        pidFile = pathlib.Path(IPF_VAR_PATH,"daemon_test.pid")
        stdoutFile = pathlib.Path(IPF_VAR_PATH,"daemon_test.stdout")
        stderrFile = pathlib.Path(IPF_VAR_PATH,"daemon_test.stderr")
        super().__init__(pidfile=pidFile,stdout=stdoutFile,stderr=stderrFile)

    def run(self):
        for i in range(0,10):
            print("printing to stdout")
        time.sleep(10)
        for i in range(0,10):
            sys.stdout.write("writing to stdout\n")
        time.sleep(10)
        for i in range(0,10):
            sys.stderr.write("writing to stderr\n")
        time.sleep(10)
        print("test done")
        
##############################################################################################################

if __name__ == "__main__":
    daemon = TestDaemon()
    daemon.start()
