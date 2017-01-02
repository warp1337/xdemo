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
from sys import platform
from socket import gethostname

# PSUTIL
import psutil as ps


def get_operating_system():
    os_system = platform.strip()
    if os_system == 'linux2':
        return 'posix'
    else:
        return os_system


def get_localhost_name():
    return gethostname().strip()


def is_file(_file):
    return os.path.isfile(_file)


def get_path_from_file(_file):
    return os.path.dirname(os.path.abspath(_file)).strip()


def get_file_from_path(_path):
    return os.path.basename(_path).strip()


def stop_all_components(_log, _sessions):
    for proc in ps.process_iter():
        if proc.name() == 'screen':
            screen_name = proc.cmdline()[3]
            if screen_name in _sessions.keys():
                raw_children = ps.Process.children(proc, recursive=True)
                # Skip the first entry, that's the initial bash
                for child in raw_children[1:]:
                    try:
                        _log.debug("[os] stopping '%s'" % child.name())
                        child.terminate()
                    except Exception, e:
                        _log.warning("[os] '%s'" % e)
                gone, still_alive = ps.wait_procs(raw_children[1:], timeout=2.0, callback=None)
                if len(still_alive) > 0:
                    _log.debug("[os] proc for '%s' still alive killing it now" % _sessions[screen_name].info_dict['component_name'])
                for child in still_alive:
                    try:
                        _log.debug("[os] killing '%s'" % child.name())
                        child.kill()
                    except Exception, e:
                        _log.warning("[os] '%s'" % e)


def get_all_component_os_info(_log, _sessions):
    for proc in ps.process_iter():
        if proc.name() == 'screen':
            screen_name = proc.cmdline()[3]
            if screen_name in _sessions.keys():
                raw_children = ps.Process.children(proc, recursive=True)
                screen_pid = proc.pid
                children = []
                for child in raw_children:
                    try:
                        children.append({child.name(): child.pid})
                    except Exception, e:
                        _log.error("[os] process for '%s' %s" % _sessions[screen_name].info_dict['component_name'], e)
                _sessions[screen_name].info_dict['osinfo'] = {"screepid": screen_pid, "children": children}
                if len(children) <= 1:
                    if _sessions[screen_name].info_dict['component_status'] == "running" or _sessions[screen_name].info_dict['component_status'] == "unknown":
                        _log.warning("[os] '%s' exited" % _sessions[screen_name].info_dict['component_name'])
                    _sessions[screen_name].info_dict['component_status'] = "stopped"
                else:
                    _sessions[screen_name].info_dict['component_status'] = "running"


def get_component_os_info(_log, _session):
    for proc in ps.process_iter():
        if proc.name() == 'screen':
            screen_name = proc.cmdline()[3]
            if screen_name in _session.name:
                raw_children = ps.Process.children(proc, recursive=True)
                screen_pid = proc.pid
                children = []
                for child in raw_children:
                    try:
                        children.append({child.name(): child.pid})
                    except Exception, e:
                        _log.error("[os] process for '%s' %s" % _session.info_dict['component_name'], e)
                _session.info_dict['osinfo'] = {"screenpid": screen_pid, "children": children}
                if len(children) <= 1:
                    if _session.info_dict['component_status'] == "running" or _session.info_dict['component_status'] == "unknown":
                        _log.debug("[os] '%s' exited" % _session.info_dict['component_name'])
                    _session.info_dict['component_status'] = "stopped"
                    return 0
                else:
                    _session.info_dict['component_status'] = "running"
                    return len(children)
    # In case no process found for the screen session it must be gone, which is bad.
    _session.info_dict['screen_status'] = "gone"
    return -2


def get_process_resource(_pid):
    p = ps.Process(_pid)
    if p.is_running:
        cpu_percent = p.cpu_percent(interval=1)
    else:
        cpu_percent = 0.0

    return cpu_percent
