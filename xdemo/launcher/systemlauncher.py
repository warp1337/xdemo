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
import time
import multiprocessing

# SELF
from xdemo.processexecution.process_executor import ProcessExecutorTread
from xdemo.utilities.ssh import kill_single_task, get_process_pid_from_remote_host


class SystemLauncher:

    def __init__(self, _system_instance, _log):
        self.log = _log
        self.executor_list = []
        self.system_instance = _system_instance
        self.collect_components_and_groups()

    def collect_components_and_groups(self):
        for item in self.system_instance.instance_flat_executionlist:
            pid_queue = multiprocessing.Queue()
            exit_queue = multiprocessing.Queue()
            pet = ProcessExecutorTread(item, self.system_instance, exit_queue, pid_queue, self.log)
            self.executor_list.append(pet)

    def deploy_tasks(self, _ready_queue):

        tree = "|"

        for executor in self.executor_list:
            tree += "-"
            if executor.type == "component":
                local_pid = None
                now = time.time()
                host = executor.get_executionhost()
                cmd = executor.get_task_cmd()
                name = executor.get_task_name()
                # Make this a command line option
                timeout = 2

                if executor.task.blockexecution is True:

                    executor.start()

                    while time.time() - now <= timeout:
                        if len(executor.job_queue._running) < 1:
                            pass
                        else:
                            local_pid = executor.job_queue._running[0].pid
                            break
                        # Save some CPU cycles, 10ms
                        time.sleep(0.01)

                    # After timeout has been reached --->
                    if local_pid is not None:
                        self.log.info("spawning %s@%s [LOCAL PID %s] [blocking] [OK]" % (name, host, local_pid))
                        self.log.info(tree + " %s" % cmd)
                        # Be careful this is the local multiprocess PID!
                        executor.set_pid(local_pid)
                    else:
                        self.log.info("%s [LPID %s] [ERROR]" % (cmd, local_pid))
                        executor.set_pid(None)

                else:

                    executor.start()
                    local_pid = executor.job_queue._running[0].pid

                    if local_pid is not None:
                        # Be careful this is the local multiprocess PID!
                        self.log.info("spawning %s@%s [LOCAL PID %s] [blocking] [OK]" % (name, host, local_pid))
                        self.log.info(tree + " %s" % cmd)
                        executor.set_pid(local_pid)
                    else:
                        self.log.error("%s [LPID %s] [ERROR]" % (cmd, local_pid))
                        executor.set_pid(None)

            # Save some CPU cycles, 10ms
            time.sleep(0.01)

        # Launched all tasks
        is_ready = True
        _ready_queue.put(is_ready)

        time.sleep(5)
        self.stop_all_tasks()

    def stop_all_tasks(self):
        self.log.info("[deployer] stopping tasks now [OK]")
        for task in self.executor_list:
            if task.type == "component":
                if not task.set_pid_queue.empty():
                    pid = task.set_pid_queue.get()
                    # Is it running?
                    if pid is not None:
                        host = task.get_executionhost()
                        uuid = task.get_task_uuid()
                        name = task.get_task_name()
                        running = task.is_alive()
                        if not running:
                            self.log.info("[%s] %s already stopped [OK]" % (host, name))
                        exit_signal = True
                        # Signal the internal job queue that an external exit was requested
                        task.exit_signal_queue.put(exit_signal)
                        # Get the actual PID
                        pid, err = get_process_pid_from_remote_host(host, uuid)
                        # Now stop the task
                        kill_single_task(host, pid)
                else:
                    self.log.error("pid queue is empty")


