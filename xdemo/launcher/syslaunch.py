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
import sys
import time
from pprint import pprint
from threading import RLock


class SystemLauncherClient:
    def __init__(self, _system_instance, _screen_pool, _log):
        self.log = _log
        self.rlock = RLock()
        self.screen_pool = _screen_pool
        self.all_screen_session_pids = None
        self.hierarchical_session_list = []
        self.hierarchical_component_list = []
        self.system_instance = _system_instance
        self.base_path = self.system_instance.base_path
        self.local_hostname = _system_instance.local_hostname
        self.local_platform = _system_instance.local_platform
        self.runtimeenvironment = _system_instance.runtimeenvironment

    def dict_print(self, _dict):
        pprint(_dict)

    def stop_all_initcriteria(self):
        for item in self.hierarchical_component_list:
            values = item.values()
            for component in values:
                for obs in component.initcriteria:
                     obs.keep_running = False

    def inner_mk_session(self, _component):
        component_host = _component.executionhost
        if component_host == self.local_hostname:
            # DO NOT CHANGE THE NAMING PATTERN OR ALL HELL BREAKS LOSE
            # SEE: screen.id and how it is constructed in the system class
            component_name = _component.name
            screen_name = _component.screen_id
            exec_script = _component.execscript
            info_dict = {"component_name": component_name,
                         "exec_script": exec_script,
                         "screen_session_name": screen_name,
                         "osinfo": {"children": [], "init_bash": None, "pid": None}
                         }
            new_screen_session = self.screen_pool.new_screen_session(screen_name, self.runtimeenvironment, info_dict)
            if new_screen_session is not None:
                source_exec_script_cmd = ". " + exec_script
                new_screen_session.send_commands(source_exec_script_cmd)

    def mk_screen_sessions(self):
        # Empty row before detach, simply looks good.
        print ""
        for item in self.system_instance.flat_execution_list:
            if 'component' in item.keys():
                component = item['component']
                self.inner_mk_session(component)
            if 'group' in item.keys():
                for component in item['group'].flat_execution_list:
                    self.inner_mk_session(component)

        self.deploy_commands()
        self.screen_pool.start()

    def inner_deploy(self, _component, _executed_list_components, _type):
        # Name is actually derived from the path: component_something.yaml
        component_name = _component.name
        cmd = "start &"
        platform = _component.platform
        host = _component.executionhost
        final_cmd = self.construct_command(host, platform, cmd, component_name, True, True)
        if final_cmd is None:
            return
        else:
            screen_name = _component.screen_id
            if screen_name not in _executed_list_components.keys():
                # Logfile has been created, we can safely start initcriteria
                # Now deploy the command in the screen session
                self.screen_pool.send_cmd(screen_name, final_cmd, _type, component_name)

                for initcriteria in _component.initcriteria:
                    initcriteria.start()

                informed_item = {screen_name: _component}
                self.hierarchical_component_list.append(informed_item)
                _executed_list_components[screen_name] = "started"

                status = self.screen_pool.get_session_status(screen_name)

                if status is None:
                    if _type == 'component':
                        self.log.error(
                            "    o---[launcher] '%s' screen session disappeared" % component_name)
                    else:
                        self.log.error(
                            "\t\to---[launcher] '%s' screen session disappeared" % component_name)

                if status == 0:
                    if _type == 'component':
                        self.log.obswar("    o---[launcher] '%s' already exited" % component_name)
                    else:
                        self.log.obswar("\t\to---[launcher] '%s' already exited" % component_name)

                if status > 0:
                    if _type == 'component':
                        self.log.obsok("    o---[launcher] '%s' pid found" % component_name)
                    else:
                        self.log.obsok("\t\to---[launcher] '%s' pid found" % component_name)

                blocking_initcriteria = len(_component.initcriteria)

                if blocking_initcriteria > 0:
                    if _type == 'component':
                        self.log.info("    o---[criteria] %d pending" % blocking_initcriteria)
                    else:
                        self.log.info("\t\to---[criteria] %d pending" % blocking_initcriteria)

                while blocking_initcriteria > 0:
                    for initcriteria in _component.initcriteria:
                        if initcriteria.is_alive():
                            time.sleep(0.001)
                            continue
                        else:
                            if initcriteria.ok is True:
                                if _type == 'component':
                                    self.log.obsok("    o---[criteria] found '%s'" % initcriteria.criteria)
                                else:
                                    self.log.obsok("\t\to---[criteria] found '%s'" % initcriteria.criteria)
                            else:
                                if _type == 'component':
                                    self.log.obswar("    o---[criteria] missing '%s'" % initcriteria.criteria)
                                else:
                                    self.log.obswar("\t\to---[criteria] missing '%s'" % initcriteria.criteria)
                            blocking_initcriteria -= 1
                            _component.initcriteria.remove(initcriteria)
                            self.log.debug("[criteria] waiting for %d criteria" % blocking_initcriteria)

            else:
                self.log.warning("[launcher] skipping '%s' on %s --> duplicate in components/groups ?" %
                                 (component_name, self.local_hostname))

    def deploy_commands(self):
        executed_list_components = {}
        executed_list_groups = {}
        for item in self.system_instance.flat_execution_list:
            if 'component' in item.keys():
                _type = 'component'
                component = item['component']
                self.inner_deploy(component, executed_list_components, _type)
            if 'group' in item.keys():
                _type = 'group'
                group_name = item['group'].name
                if group_name not in executed_list_groups.keys():
                    executed_list_groups[group_name] = "started"
                    self.log.info("[group] descending into '%s'" % item['group'].name)
                    for component in item['group'].flat_execution_list:
                        self.inner_deploy(component, executed_list_components, _type)
                else:
                    self.log.warning(
                        "[launcher] skipping '%s' on %s --> duplicate in components/groups ?" %
                        (item['group'].name, self.local_hostname))

    def construct_command(self, _host, _platform, _cmd, _component, _requires_x=None, _requires_remote_x=None):
        if _platform != self.local_platform:
            self.log.warning("[launcher] skipping '%s'?! what, running %s component on %s?" % (_component,
                                                                                              _platform,
                                                                                              self.local_platform))
            return None
        if _host == self.local_hostname:
            return _cmd.strip()
        else:
            self.log.debug("[launcher] skipping %s | host %s | platform %s" % (_component,
                                                                               _host,
                                                                               _platform))
            return None
