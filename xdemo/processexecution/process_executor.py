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

#STD
import os
import uuid
import time
import StringIO
from threading import Thread

# Fabric
from fabric.api import run, settings, env
from fabric.network import disconnect_all


class ProcessExecutor(Thread):

    def __init__(self, _component_or_group, _system_instance):

        Thread.__init__(self)
        self.type = None
        self.keeprunning = True
        self.commandprefix = ""
        self.uuid = str(uuid.uuid4())
        self.outputpipe = StringIO.StringIO()
        self.system_instance = _system_instance
        self.base_path = _system_instance.base_path

        if 'group' in _component_or_group:
            self.type = "grouplauncher"
            self.target = _component_or_group['group']
        else:
            self.type = "componentlauncher"
            self.target = _component_or_group['component']

    def stage_execution_environment(self):
        if self.type == "componentlauncher":
            env.shell_env["xdemoid"] = self.uuid
            env.shell_env["DISPLAY"] = ":0.0"
            if self.target.platform == 'linux':
                self.commandprefix = "source " + self.base_path + "/" + self.system_instance.runtimeenvironment['linux'] + " && "
            if self.target.platform == 'darwin':
                self.commandprefix = "source " + self.base_path + "/" + self.system_instance.runtimeenvironment['darwin'] + " && "
            if self.target.platform == 'windows':
                # How does windows load an environment, I dont know...
                pass

    def task(self, _cmd):
        self.stage_execution_environment()
        with settings(host_string=self.target.executionhost, forward_agent=True):
            run(_cmd, shell=True, stdout=self.outputpipe, stderr=self.outputpipe)

    def get_task_output(self):
        return self.outputpipe

    def get_task_uuid(self):
        return self.uuid

    def stop_execution(self):
        self.keeprunning = False
        disconnect_all()

    def run(self):
        if self.type == "componentlauncher":
            cmd = self.commandprefix + str(self.target.command)
            while self.keeprunning:
                self.task(cmd)


