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
from xdemo.utilities.generics import represents_int
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
            remote_pid_queue = multiprocessing.Queue()
            pet = ProcessExecutorTread(item, self.system_instance, exit_queue, pid_queue, remote_pid_queue, self.log)
            self.executor_list.append(pet)

    def deploy_tasks(self, _ready_queue):

        tree = "|"

        for executor in self.executor_list:
            tree += "-"
            if executor.type == "component":
                local_pid = None
                remote_pid = None
                now = time.time()
                host = executor.get_executionhost()
                cmd = executor.get_task_cmd()
                name = executor.get_task_name()
                uuid = executor.get_task_uuid()
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
                        # self.log.debug("spawning %s@%s [LOCAL PID %s] [blocking] [OK]" % (name, host, local_pid))
                        self.log.debug("deploying %s@%s [blocking]" % (name, host))
                        self.log.debug(tree + " %s" % cmd)
                        # Be careful this is the local multiprocess PID!
                        executor.set_pid(local_pid)
                    else:
                        self.log.info("%s  no LOCAL PID found [ERROR]" % (cmd))
                        executor.set_pid(None)

                    #--------------------------------------------------------------------------------------------------#

                    while time.time() - now <= timeout:
                        tmp_pid = get_process_pid_from_remote_host(host, uuid)[0]
                        print tmp_pid
                        if not represents_int(tmp_pid):
                            pass
                        else:
                            remote_pid = tmp_pid
                            break
                        # Save some CPU cycles, 100ms
                        time.sleep(0.1)

                    # After timeout has been reached --->
                    if remote_pid is not None and remote_pid != "" and represents_int(remote_pid):
                        # self.log.debug("spawning %s@%s [LOCAL PID %s] [blocking] [OK]" % (name, host, local_pid))
                        self.log.info("deployed %s@%s [PID %s] [blocking] [OK]" % (name, host, remote_pid))
                        self.log.info(tree + " %s" % cmd)
                        # Be careful this is the local multiprocess PID!
                        executor.set_remote_pid(remote_pid)
                    else:
                        self.log.error("%s no REMOTE PID found [ERROR]" % cmd)
                        executor.set_remote_pid(None)

                else:

                    executor.start()
                    remote_pid = get_process_pid_from_remote_host(host, uuid)[0]

                    if remote_pid is not None and remote_pid != "" and represents_int(remote_pid):
                        # self.log.debug("spawning %s@%s [LOCAL PID %s] [blocking] [OK]" % (name, host, local_pid))
                        self.log.info("deployed %s@%s [PID %s] [blocking] [OK]" % (name, host, remote_pid))
                        self.log.info(tree + " %s" % cmd)
                        # Be careful this is the local multiprocess PID!
                        executor.set_remote_pid(remote_pid)
                    else:
                        self.log.error("%s no REMOTE PID found [ERROR]" % cmd)
                        executor.set_remote_pid(None)

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
                if not task.set_pid_queue.empty() and not task.set_remote_pid_queue.empty():
                    local_pid = task.set_pid_queue.get()
                    remote_pid = task.set_remote_pid_queue.get()
                    print local_pid, remote_pid
                    # Is it running?
                    if represents_int(local_pid) and represents_int(remote_pid):
                        host = task.get_executionhost()
                        name = task.get_task_name()
                        running = task.is_alive()
                        # Local thread is not running, we still want to kill the children
                        if not running:
                            self.log.warning("[%s] %s already stopped" % (host, name))
                        exit_signal = True
                        # Signal the internal job queue that an external exit was requested
                        task.exit_signal_queue.put(exit_signal)
                        # Now stop the task
                        kill_single_task(host, remote_pid)
                else:
                    self.log.error("pid queue is empty [ERROR]")


