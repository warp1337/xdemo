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
import StringIO
import threading

# Fabric
from fabric.api import run, settings, env
from fabric.network import disconnect_all


class ProcessExecutor:

    def __init__(self, _host, _platform):
        self.environment = {}
        self.uuid = str(uuid.uuid4())
        self.outputpipe = StringIO.StringIO()
        self.host = str(_host).strip().lower()
        self.platform = str(_platform).strip().lower()

    def stage_execution_environment(self):
        env.shell_env["xdemoid"] = self.uuid
        env.shell_env["DISPLAY"] = ":0.0"

    def task(self, _cmd):
        self.stage_execution_environment()
        with settings(host_string=self.host, forward_agent=True):
            run(_cmd, shell=True, stdout=self.outputpipe, stderr=self.outputpipe)

    def get_task_output(self):
        return self.outputpipe

    def get_task_uuid(self):
        return self.uuid


if __name__ == '__main__':

    gpe = ProcessExecutor("localhost", "linux")
    if gpe.platform == 'linux':
        # t = threading.Thread(target=gpe.task, args=("export DISPLAY=:0; ls -la & echo $!",))
        t = threading.Thread(target=gpe.task, args=("gedit",))
        t.start()
        t.join()
        task_output = gpe.get_task_output()
        task_output.getvalue()

    disconnect_all()


