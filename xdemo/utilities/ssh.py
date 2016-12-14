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

import os
import subprocess
from subprocess import PIPE


def get_process_pid_from_remote_host(_host, _uuid):
    ssh_cmd = "ssh " + os.environ["USER"] + "@" + _host + " 'pgrep -f %s'" % _uuid
    proc = subprocess.Popen(ssh_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    out_arr = out.split("\n")
    return out_arr[0], err


def kill_single_task(_host, _pid):
    FNULL = open(os.devnull, 'w')
    # ssh_cmd = "ssh " + os.environ["USER"] + "@" + _host + " 'kill -s SIGINT %s' " % str(_pid)
    ssh_cmd = "ssh " + os.environ["USER"] + "@" + _host + " 'kill %s' " % str(_pid)
    proc = subprocess.Popen(ssh_cmd, shell=True, stdout=FNULL, stderr=FNULL)