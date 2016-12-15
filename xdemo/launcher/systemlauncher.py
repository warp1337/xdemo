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
import os
import time
import multiprocessing

# SELF
from xdemo.utilities.generics import represents_int
from xdemo.processexecution.process_executor import ProcessExecutorTread
from xdemo.utilities.ssh import kill_single_task

class SystemLauncher:

    def __init__(self, _system_instance, _screen_pool, _log):
        self.log = _log
        self.screen_pool = _screen_pool
        self.hierarchical_session_list = []
        self.introspection_host_sessions = []
        self.system_instance = _system_instance
        self.ssh_template = "ssh -tt -C " + os.environ['USER'] + "@X@ 'echo $$; exec "
        self.ssh_template_x = "ssh -tt -C " + os.environ['USER'] + "@X@ 'echo $$; export DISPLAY=:0; exec "
        # This need debugging
        self.ssh_template_rx = "ssh -tt -C " + os.environ['USER'] + "@X@ 'echo $$; export DISPLAY=X@:0; exec "

    def mk_screen_sessions(self):
        for item in self.system_instance.instance_flat_executionlist:
            if 'component' in item.keys():
                name = item['component'].name.strip()
                system_uuid = item['component'].uuid.strip()
                uuid = self.mk_id(name, system_uuid)
                new_screen_session = self.screen_pool.new_screen_session(uuid)
                informed_item = {str(uuid): new_screen_session}
                self.hierarchical_session_list.append(informed_item)
                host = item['component'].executionhost
                for hosts in self.introspection_host_sessions:
                    if 'host' in hosts.keys():
                        pass
                    else:
                        new_screen_session = self.screen_pool.new_screen_session(host)
                        informed_item = {str(host): new_screen_session}
                        self.introspection_host_sessions.append(informed_item)

    def deploy_commands(self):
        for item in self.system_instance.instance_flat_executionlist:
            if 'component' in item.keys():
                name = item['component'].name.strip()
                system_uuid = item['component'].uuid.strip()
                uuid = self.mk_id(name,  system_uuid)
                cmd = item['component'].command
                platform = item['component'].platform
                host = item['component'].executionhost
                final_cmd = self.construct_command(host, platform, cmd, True, True)
                self.screen_pool.send_cmd(uuid, final_cmd)

    def construct_command(self, _host, _platform, _cmd, _requires_x=None, _requires_remote_x=None):
        if self.clean_str(_platform) == 'linux':
            if self.clean_str(_host) == 'localhost':
                return _cmd.strip()
            else:
                tmp_cmd = self.ssh_template.replace("X@", self.clean_str(_host))
            if _requires_x is not None:
                tmp_cmd = self.ssh_template_x.replace("X@", self.clean_str(_host))
            if _requires_remote_x is not None:
                tmp_cmd = self.ssh_template_rx.replace("X@", self.clean_str(_host))
            final_cmd = tmp_cmd + _cmd.strip() + "'"
            return final_cmd

    @staticmethod
    def clean_str(_input_string):
        return _input_string.strip().lower()

    def mk_id(self, _name, _uuid):
        return self.clean_str(_name) + "-" + self.clean_str(_uuid)

    def is_component_alive(self, _uuid):
        # return self.screen_pool.get_screen_status(_uuid)
        pass

    # def deploy_tasks(self, _ready_queue):
    #
    #     tree = "|"
    #
    #     # Get the local PID of the multiprocess spawning the SSH session
    #     for executor in self.executor_list:
    #         tree += "-"
    #         if executor.type == "component":
    #             local_pid = None
    #             now = time.time()
    #             cmd = executor.get_task_cmd()
    #             name = executor.get_task_name()
    #             host = executor.get_executionhost()
    #             # Make this a command line option
    #             timeout = 2
    #
    #             if executor.task.blockexecution is True:
    #                 executor.start()
    #
    #                 while time.time() - now <= timeout:
    #                     if len(executor.job_queue._running) < 1:
    #                         pass
    #                     else:
    #                         local_pid = executor.job_queue._running[0].pid
    #                         break
    #                     # Save some CPU cycles, 10ms
    #                     time.sleep(0.01)
    #
    #                 # After timeout has been reached --->
    #                 if local_pid is not None and local_pid != "" and represents_int(local_pid):
    #                     self.log.debug("deploying %s@%s [blocking]" % (name, host))
    #                     self.log.debug(tree + " %s" % cmd)
    #                     # Be careful this is the local multiprocess PID!
    #                     executor.set_local_pid(local_pid)
    #                 else:
    #                     self.log.info("%s  no LOCAL PID found [ERROR]" % cmd)
    #                     executor.set_local_pid(None)
    #
    #             else:
    #                 executor.start()
    #                 local_pid = executor.job_queue._running[0].pid
    #
    #                 if local_pid is not None and local_pid != "" and represents_int(local_pid):
    #                     # Be careful this is the local multiprocess PID!
    #                     executor.set_local_pid(local_pid)
    #                 else:
    #                     self.log.info("%s  no LOCAL PID found [ERROR]" % cmd)
    #                     executor.set_local_pid(None)
    #
    #         # Save some CPU cycles, 10ms
    #         time.sleep(0.01)
    #
    #     # Launched all tasks
    #     is_ready = True
    #     _ready_queue.put(is_ready)
    #
    # def stop_all_tasks(self):
    #     self.log.info("[deployer] stopping tasks now [OK]")
    #     for task in self.executor_list:
    #         if task.type == "component":
    #             if not task.get_local_pid_queue().empty():
    #                 local_pid = task.get_local_pid()
    #                 if represents_int(local_pid):
    #                     uuid = task.get_task_uuid()
    #                     name = task.get_task_name()
    #                     host = task.get_executionhost()
    #                     # Local thread is not running, we still want to kill the children
    #                     if not task.get_stop_queue().empty():
    #                         self.log.warning("[%s] %s already stopped" % (host, name))
    #                     exit_signal = True
    #                     # Signal the internal job queue that an external exit was requested
    #                     task.exit_signal_queue.put(exit_signal)
    #                     # Now stop the task
    #                     kill_single_task(host, uuid)
    #             else:
    #                 self.log.error("local pid queue is empty [ERROR]")

