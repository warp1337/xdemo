"""

This file is part of XDEMO

Copyright(c) <Florian Lier>
https://github.com/warp1337/xdemo

This file may be licensed under the terms of the
GNU Lesser General Public License Version 3 (the ``LGPL''),
or (at your option) any later version.

Software distributed under the License is distributed
on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
express or implied. See the LGPL for the specific language
governing rights and limitations.

You should have received a copy of the LGPL along with this
program. If not, go to http://www.gnu.org/licenses/lgpl.html
or write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

The development of this software was supported by the
Excellence Cluster EXC 277 Cognitive Interaction Technology.
The Excellence Cluster EXC 277 is a grant of the Deutsche
Forschungsgemeinschaft (DFG) in the context of the German
Excellence Initiative.

Authors: Florian Lier
<flier>@techfak.uni-bielefeld.de

"""

# STD
import uuid
import StringIO
import multiprocessing
from threading import Thread

# FABRIC
from fabric.api import *
from fabric.job_queue import JobQueue
from fabric.network import disconnect_all

# SELF
from xdemo.container.fabpatch import execute_fab_patch


class ProcessExecutor(Thread):

    def __init__(self, _component_or_group, _system_instance, _log):

        Thread.__init__(self)
        self.log = _log
        self.type = None
        self.pool_size = 1
        self.keep_running = True
        self.command_prefix = ""
        self.uuid = str(uuid.uuid4())
        self.queue = multiprocessing.Queue()
        self.output_pipe = StringIO.StringIO()
        self.system_instance = _system_instance
        self.base_path = _system_instance.base_path
        self.job_queue = JobQueue(self.pool_size, self.queue)

        if 'group' in _component_or_group:
            self.type = "group"
            self.target = _component_or_group['group']
        else:
            self.type = "component"
            self.target = _component_or_group['component']

    def stage_execution_environment(self, _cmd):
        if self.type == "component":
            env.shell_env["xdemoid"] = self.uuid
            env.shell_env["DISPLAY"] = ":0.0"
            if self.target.platform == 'linux':
                self.command_prefix = "source " + self.base_path + "/" + self.system_instance.runtimeenvironment['linux'] + " && "
                return self.command_prefix + _cmd
            if self.target.platform == 'darwin':
                self.command_prefix = "source " + self.base_path + "/" + self.system_instance.runtimeenvironment['darwin'] + " && "
                return self.command_prefix + _cmd
            if self.target.platform == 'windows':
                # How does windows load an environment, I dont know...
                return ""

    def do(self, _cmd):

        @parallel
        def task_thread(_raw_cmd):
            full_cmd = self.stage_execution_environment(_raw_cmd)
            with settings(host_string=self.target.executionhost, forward_agent=True, connection_attempts=5):
                return_values = run(full_cmd, shell=True, stdout=self.output_pipe, stderr=self.output_pipe, quiet=True)
                self.log.info("task returned")
                self.log.info(full_cmd)
                self.log.info("return code %s, failed: %s, succeeded: %s" % (return_values.return_code,
                                                                             return_values.failed,
                                                                             return_values.succeeded))
                self.log.info("-----------------")

        @task
        def deploy():
            env.shell_env["xdemoid"] = self.uuid
            env.shell_env["DISPLAY"] = ":0.0"
            host_list = [self.target.executionhost]
            execute_fab_patch(task_thread, self.queue, self.job_queue, self.log, _cmd, hosts=host_list)

        deploy()

    def get_task_output(self):
        return self.output_pipe

    def get_task_uuid(self):
        return self.uuid

    def stop_execution(self):
        self.keep_running = False

    @staticmethod
    def disconnect_task():
        disconnect_all()

    def run(self):
        if self.type == "component":
            cmd = self.command_prefix + self.target.command
            self.do(cmd)


class SimpleProcessExecutor(Thread):

    def __init__(self, _command, _host, _log):

        Thread.__init__(self)
        self.log = _log
        self.cmd = _command
        self.host = _host
        self.pool_size = 1
        self.uuid = str(uuid.uuid4())
        self.queue = multiprocessing.Queue()
        self.output_pipe = StringIO.StringIO()
        self.job_queue = JobQueue(self.pool_size, self.queue)

    def do(self, _cmd):

        @parallel
        def task_thread(_cmd):
            with settings(host_string=self.host, forward_agent=True, connection_attempts=5):
                return_values = run(_cmd, shell=True, stdout=self.output_pipe, stderr=self.output_pipe, quiet=True)
                self.log.info("task returned")
                self.log.info(_cmd)
                self.log.info("return code %s, failed: %s, succeeded: %s" % (return_values.return_code,
                                                                             return_values.failed,
                                                                             return_values.succeeded))
                self.log.info("-----------------")

        @task
        def deploy():
            env.shell_env["xdemoid"] = self.uuid
            env.shell_env["DISPLAY"] = ":0.0"
            host_list = [self.host]
            execute_fab_patch(task_thread, self.queue, self.job_queue, self.log, self.cmd, hosts=host_list)

        deploy()

    def get_task_output(self):
        return self.output_pipe

    def get_task_uuid(self):
        return self.uuid

    @staticmethod
    def disconnect_task():
        disconnect_all()

    def run(self):
        self.do(self.cmd)