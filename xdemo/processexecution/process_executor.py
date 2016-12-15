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

# SELF
from xdemo.fabpatch.adaptations import execute_fab_patch


class ProcessExecutorTread(Thread):

    def __init__(self, _component_or_group,
                 _system_instance,
                 _exit_signal_queue,
                 _set_pid_queue,
                 _set_remote_pid_queue,
                 _log):

        Thread.__init__(self)
        self.log = _log
        self.type = None
        self.pool_size = 1
        self.command_prefix = ""
        self.uuid = str(uuid.uuid4())
        self.set_pid_queue = _set_pid_queue
        self.queue = multiprocessing.Queue()
        self.output_pipe = StringIO.StringIO()
        self.system_instance = _system_instance
        self.cmd_queue = multiprocessing.Queue()
        self.set_remote_pid_queue = _set_remote_pid_queue
        self.exit_signal_queue = _exit_signal_queue
        self.base_path = _system_instance.base_path
        self.job_queue = JobQueue(self.pool_size, self.queue)

        if 'group' in _component_or_group:
            self.type = "group"
            self.task = _component_or_group['group']
            self.name = self.task.name
            self.cmd = self.task.command
        else:
            self.type = "component"
            self.task = _component_or_group['component']
            self.name = self.task.name
            self.cmd = self.task.command
            self.executionhost = self.task.executionhost

    def stage_execution_environment(self, _cmd):
        if self.type == "component":
            env.shell_env["xdemoid"] = self.uuid
            env.shell_env["DISPLAY"] = ":0.0"
            if self.task.platform == 'linux':
                self.command_prefix = "source " + self.base_path + "/" + self.system_instance.runtimeenvironment['linux'] + " && "
                return self.command_prefix + _cmd
            if self.task.platform == 'darwin':
                self.command_prefix = "source " + self.base_path + "/" + self.system_instance.runtimeenvironment['darwin'] + " && "
                return self.command_prefix + _cmd
            if self.task.platform == 'windows':
                # How does windows load an environment, I dont know...
                return ""

    def do(self, _cmd):

        @parallel
        def task_thread(_raw_cmd, _name):
            full_cmd = self.stage_execution_environment(_raw_cmd)
            with settings(host_string=self.task.executionhost, forward_agent=True, connection_attempts=5):
                return_values = run(full_cmd, shell=True, stdout=self.output_pipe, stderr=self.output_pipe, quiet=True)

                if self.exit_signal_queue.empty():
                    self.log.warning("[%s] %s task returned" % (self.task.executionhost, _name))
                    self.log.debug(full_cmd)
                    if return_values.failed:
                        self.log.error("|- return code %s, failed: %s, succeeded: %s" % (return_values.return_code,
                                                                                         return_values.failed,
                                                                                         return_values.succeeded))
                    else:
                        self.log.warning("|- return code %s, failed: %s, succeeded: %s" % (return_values.return_code,
                                                                                           return_values.failed,
                                                                                           return_values.succeeded))
                else:
                    self.log.info("[%s] %s was stopped [OK]" % (self.task.executionhost, _name))
                    self.log.debug(full_cmd)

        @task
        def deploy():
            env.shell_env["xdemoid"] = self.uuid
            env.shell_env["DISPLAY"] = ":0.0"
            host_list = [self.task.executionhost]
            execute_fab_patch(task_thread, self.queue, self.job_queue, self.exit_signal_queue, self.log,
                              _cmd, self.name, hosts=host_list)

        deploy()

    def set_pid(self, _pid):
        self.set_pid_queue.put(_pid)

    def set_remote_pid(self, _pid):
        self.set_remote_pid_queue.put(_pid)

    def get_task_output(self):
        return self.output_pipe

    def get_task_uuid(self):
        return self.uuid

    def get_task_name(self):
        return self.name

    def get_task_cmd(self):
        return self.cmd

    def get_executionhost(self):
        return self.executionhost

    def run(self):
        if self.type == "component":
            self.cmd_queue.put(self.cmd)
            self.do(self.cmd)
            self.log.info("%s thread exited" % self.name)
