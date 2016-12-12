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

import time
from xdemo.processexecution.process_executor import ProcessExecutor


class SystemLauncher:

    def __init__(self, _systeminstance, _log):
        self.log = _log
        self.system_instance = _systeminstance
        self.executor_list = []

        self.collect_components_and_groups()
        self.iterate()

    def collect_components_and_groups(self):
        for item in self.system_instance.flat_executionlist:
            self.log.debug("execution iterator")
            self.log.debug(item)
            self.log.debug("-----------------")
            pe = ProcessExecutor(item, self.system_instance)
            self.executor_list.append(pe)

    def iterate(self):
        for exe in self.executor_list:
            if exe.type == "componentlauncher":
                exe.start()

        now = time.time()
        while time.time() - now <= 5:
            time.sleep(1)
        for exe in self.executor_list:
            if exe.type == "componentlauncher":
                exe.stop_execution()

        print "Exit"
