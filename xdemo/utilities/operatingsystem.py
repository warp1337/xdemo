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
from socket import gethostname

# PSUTIL
import psutil as ps


def get_operating_system():
    return os.name.strip()


def get_localhost_name():
    return gethostname().strip()


def is_file(_file):
    return os.path.isfile(_file)


def get_path_from_file(_file):
    return os.path.dirname(os.path.abspath(_file)).strip()


def get_file_from_path(_path):
    return os.path.basename(_path).strip()


def get_all_screen_session_pids(_log, _list_of_screen_sessions):
    session_and_pids = {}
    for p in ps.process_iter():
        if 'screen' in p.name():
            screen_command = p.cmdline()[2]
            for item in _list_of_screen_sessions:
                if item[0] == screen_command:
                    session_pid = p.pid
                    raw_children = ps.Process.children(p, recursive=True)
                    children = []
                    for child in raw_children:
                        # Don't collect the 1st child of screen which is the
                        # executing bash/sh in this case. If we would kill this
                        # shell, the screen session would exit
                        if child.pid == session_pid+1:
                            continue
                        else:
                            children.append({child.name(): child.pid})
                    session_and_pids[item[0]] = {"screen_name": item[0],
                                                 "pid": session_pid,
                                                 "children": children,
                                                 "component_name": item[1]}
    if len(_list_of_screen_sessions) != len(session_and_pids.keys()):
        _log.error("[ps] could find PIDS of all screen sessions")
    else:
        return session_and_pids
