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
from os.path import getsize
from threading import Thread


class StdoutObserver(Thread):
    def __init__(self, _file, _log, _component_name, _criteria, _max_wait_time):
        Thread.__init__(self)
        self.ok = False
        self.log = _log
        self.file = _file
        self.keep_running = True
        self.criteria = _criteria
        self.type = "stdoutobserver"
        self.maxwaittime = _max_wait_time
        self.component_name = _component_name

    def stop(self):
        self.keep_running = False

    def run(self):
        last_size = 0
        now = time.time()
        f = open(self.file, 'r')
        while time.time() - now <= self.maxwaittime and self.ok is False and self.keep_running is True:
            cur_size = getsize(self.file)
            if cur_size != last_size:
                f.seek(last_size if cur_size > last_size else 0)
                text = f.read()
                last_size = cur_size
                if self.criteria in text:
                    self.ok = True
            else:
                pass
            # Save CPU cycles 1ms
            time.sleep(0.001)
        f.close()


class StdoutExcludeObserver(Thread):
    def __init__(self, _file, _log, _component_name, _criteria, _max_wait_time):
        Thread.__init__(self)
        self.ok = False
        self.log = _log
        self.file = _file
        self.keep_running = True
        self.criteria = _criteria
        self.maxwaittime = _max_wait_time
        self.type = "stdoutexcludeobserver"
        self.component_name = _component_name

    def stop(self):
        self.keep_running = False

    def run(self):
        last_size = 0
        now = time.time()
        f = open(self.file, 'r')
        while time.time() - now <= self.maxwaittime and self.ok is False and self.keep_running is True:
            cur_size = getsize(self.file)
            if cur_size != last_size:
                f.seek(last_size if cur_size > last_size else 0)
                text = f.read()
                last_size = cur_size
                if self.criteria not in text:
                    self.ok = True
                else:
                    self.ok = False
                    break
            else:
                pass
            # Save CPU cycles 1ms
            time.sleep(0.001)
        f.close()
