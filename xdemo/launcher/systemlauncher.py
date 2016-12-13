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

# SELF
from xdemo.processexecution.process_executor import ProcessExecutor, SimpleProcessExecutor


class SystemLauncher:

    def __init__(self, _system_instance, _log):
        self.log = _log
        self.system_instance = _system_instance
        self.executor_list = []
        self.kill_pid_list = []

        self.collect_components_and_groups()
        self.deploy_tasks()
        self.iterate_process_queues()

    def collect_components_and_groups(self):
        for item in self.system_instance.instance_flat_executionlist:
            self.log.debug("execution iterator")
            self.log.debug(item)
            self.log.debug("-----------------")
            pe = ProcessExecutor(item, self.system_instance, self.log)
            self.executor_list.append(pe)

    def deploy_tasks(self):
        for executor in self.executor_list:
            if executor.type == "component":
                now = time.time()
                host = executor.target.executionhost
                cmd = executor.target.command
                # Make this a command line option
                timeout = 30
                pid = None
                if executor.target.blockexecution is True:
                    executor.start()
                    while time.time() - now <= timeout:
                        if len(executor.job_queue._running) < 1:
                            pass
                        else:
                            pid = executor.job_queue._running[0].pid
                            self.kill_pid_list.append(pid)
                            break
                        # Save some CPU cycles, 10ms
                        time.sleep(0.01)
                    # After timeout
                    if pid is not None:
                        self.log.info("[%s] pid (%s) confirmed for %s [blocking]" % (host, pid, cmd))
                    else:
                        self.log.error("[%s] pid (%s) not found for %s [blocking]" % (host, cmd, pid))
                else:
                    executor.start()
                    pid = executor.job_queue._running[0].pid
                    self.kill_pid_list.append(pid)
                    if pid is not None:
                        self.log.info("[%s] pid (%s) confirmed for %s" % (host, pid, cmd))
                    else:
                        self.log.error("[%s] pid (%s) not found for %s" % (host, cmd, pid))
            # Save some CPU cycles, 50ms
            time.sleep(0.05)

    def iterate_job_queues(self):
        for executor in self.executor_list:
            if executor.type == "component":
                print executor.queue

    def iterate_process_queues(self):
        for executor in self.executor_list:
            if executor.type == "component":
                # print executor.job_queue._queued
                for job in executor.job_queue._running:
                    # print job.pid
                    pass

    def stop_all_tasks(self):
        for pid in self.kill_pid_list:
            cmd = "kill -2 %s" % pid
            # cmd = "gedit"
            spe = SimpleProcessExecutor(cmd, "localhost", self.log)
            spe.start()

    def disconnect_tasks(self):
        for executor in self.executor_list:
            if executor.type == "component":
                executor.disconnect_task()
