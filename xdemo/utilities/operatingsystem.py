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


def get_all_session_os_info(_log, _sessions):
    for proc in ps.process_iter():
        if proc.name() == 'screen':
            screen_name = proc.cmdline()[2]
            if screen_name in _sessions.keys():
                raw_children = ps.Process.children(proc, recursive=True)
                screen_pid = proc.pid
                init_bash = None
                children = []
                for child in raw_children:
                    if child.pid == proc.pid + 1:
                        init_bash = child.pid
                    else:
                        children.append({child.name(): child.pid})
                if init_bash is None:
                    # In this case it seems that the programm exited abnormally and the first
                    # bash vanished. There is however, another bash in that screen which does
                    # not have the PID+1. In this case kill and restart the screen session.
                    _log.error("[screen] '%s' init bash exited" % _sessions[screen_name].info_dict["component_name"])
                _sessions[screen_name].info_dict['osinfo'] = {"pid": screen_pid, "init_bash": init_bash, "children": children}


def get_session_os_info(_log, _session):
    for proc in ps.process_iter():
        if proc.name() == 'screen':
            screen_name = proc.cmdline()[2]
            if screen_name in _session.name:
                raw_children = ps.Process.children(proc, recursive=True)
                screen_pid = proc.pid
                init_bash = None
                children = []
                for child in raw_children:
                    if child.pid == proc.pid + 1:
                        init_bash = child.pid
                    else:
                        children.append({child.name(): child.pid})
                if init_bash is None:
                    # In this case it seems that the programm exited abnormally and the first
                    # bash vanished. There is however, another bash in that screen which does
                    # not have the PID+1. In this case kill and restart the screen session.
                    # Report in the launcher
                    # _log.error("[screen] '%s' init bash exited" % _session.info_dict["component_name"])
                    pass
                _session.info_dict['osinfo'] = {"pid": screen_pid, "init_bash": init_bash, "children": children}
                if len(children) < 1:
                    return 0
                elif init_bash is None:
                    return None
                else:
                    return len(children)
