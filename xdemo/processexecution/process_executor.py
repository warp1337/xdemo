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
import StringIO
import threading

# Fabric
from fabric.api import run, local, settings
from fabric.network import disconnect_all


class GenericProcessExecutor:

    def __init__(self, _host, _platform):
        self.host = str(_host).strip().lower()
        self.platform = str(_platform).strip().lower()
        self.outputpipe = StringIO.StringIO()

    def task(self, _cmd):
        with settings(host_string=self.host, forward_agent=True):
            run(_cmd, shell=True, stdout=self.outputpipe, stderr=self.outputpipe)

    def get_output(self):
        print self.outputpipe.getvalue()


if __name__ == '__main__':

    gpe = GenericProcessExecutor("localhost", "linux")
    if gpe.platform == 'linux':
        t = threading.Thread(target=gpe.task, args=("export DISPLAY=:0; ls -la",))
        o = threading.Thread(target=gpe.get_output)
        t.start()
        o.start()
        t.join()
        o.join()
    else:
        gpe.task("gedit")

    disconnect_all()


