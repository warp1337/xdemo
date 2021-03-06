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
from threading import Lock


class SSHSystemLauncherClient:
    def __init__(self, _system_instance, _screen_pool, _log, _debug_mode):
        self.log = _log
        self.lock = Lock()
        self.debug_mode = _debug_mode
        self.screen_pool = _screen_pool
        self.strict_policy_missed = False
        self.exit_allowed_missed = False
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
            self.lock.acquire()
            # DO NOT CHANGE THE NAMING PATTERN OR ALL HELL BREAKS LOSE
            # SEE: screen.id and how it is constructed in the system class
            component_name = _component.name
            screen_name = _component.screen_id
            exec_script = _component.execscript
            info_dict = { "component_name": component_name,
                          "exec_script": exec_script,
                          "screen_session_name": screen_name,
                          "osinfo": {"children": [], "screenpid": None},
                          "component_status": "unknown",
                          "screen_status": "init"
            }
            new_screen_session = self.screen_pool.new_screen_session(screen_name, self.runtimeenvironment, info_dict)
            # Add some time to spawn the session, 50ms
            time.sleep(0.05)
            result = self.screen_pool.check_exists_in_pool(screen_name)
            if result is not None:
                source_exec_script_cmd = ". " + exec_script
                new_screen_session.send_commands(source_exec_script_cmd)
            else:
                self.log.error("[launcher] '%s' could not be initialized THIS IS FATAL!" % screen_name)
                self.screen_pool.kill_all_screen_sessions()
                sys.exit(1)
            self.lock.release()

    def mk_screen_sessions(self):
        for item in self.system_instance.flat_execution_list:
            if 'component' in item.keys():
                component = item['component']
                self.inner_mk_session(component)
            if 'group' in item.keys():
                for component in item['group'].flat_execution_list:
                    self.inner_mk_session(component)
        # Start components
        self.deploy_commands()
        # Activate continuous monitoring
        if self.strict_policy_missed is False and self.exit_allowed_missed is False:
            self.screen_pool.start()
        else:
            pass

    def inner_deploy(self, _component, _executed_list_components, _type):
        # Name is actually derived from the path: component_something.yaml
        component_name = _component.name
        cmd = "start"
        platform = _component.platform
        host = _component.executionhost
        final_cmd = self.construct_command(host, platform, cmd, component_name, True, True)
        if final_cmd is None:
            return
        else:
            screen_name = _component.screen_id
            # Check if it has already been started on this host
            if screen_name not in _executed_list_components.keys():
                # Get the global lock
                self.lock.acquire()
                # Now clean the log and deploy the command in the screen session
                self.screen_pool.clean_log(screen_name)
                result = self.screen_pool.send_cmd(screen_name, final_cmd, _type, component_name)

                if result is None:
                    self.log.error("[launcher] '%s' command could not be sent" % component_name)
                    self.lock.release()
                    return

                # Add this component to the hierarchical list of started components
                informed_item = {screen_name: _component}
                self.hierarchical_component_list.append(informed_item)
                _executed_list_components[screen_name] = "started"

                # Give the process some time to spawn: 50ms
                time.sleep(0.05)

                self.log.debug("├╼[os] '%s' gathering pids" % component_name)

                # Get the status of the send_cmd()
                # status > 0   : everything is okay, session has 1 or more children [#1 is always an init bash/sh]
                # status == 0  : command exited, only the init bash/sh is present
                # status == -1 : screen session not found in session list, this is bad
                # status == -2 : no process found for screen session, this is the worst case

                status = self.screen_pool.get_session_os_info(screen_name)
                self.log.debug("  ├╼[os] '%s' children %d" % (component_name, status))

                if status > 0:
                    self.log.debug("├╼[os] '%s' is running" % component_name)

                if status == 0:
                    self.log.obswar("├╼[os] '%s' exited" % component_name)
                    if _component.exitallowed is False:
                        self.log.obserr("└╼[os] '%s' exit not allowed in config" % component_name)
                        self.exit_allowed_missed = True
                        self.lock.release()
                        return

                if status == -1:
                    self.log.debug("├╼[os] '%s' screen not in session list THIS IS BAD!" % component_name)
                    if self.debug_mode:
                        self.log.debug("[debugger] press RETURN to go on...")
                        raw_input('')

                if status == -2:
                    self.log.debug("├╼[os] '%s' no process for screen session found THIS IS REALLY BAD!" % component_name)
                    if self.debug_mode:
                        self.log.debug("[debugger] press RETURN to go on...")
                        raw_input('')

                # Logfile has been created, we can safely start init criteria threads
                for init_criteria in _component.initcriteria:
                    init_criteria.start()

                blocking_initcriteria = len(_component.initcriteria)

                if blocking_initcriteria > 0:
                    self.log.info("├╼[initcriteria] %d pending" % blocking_initcriteria)
                else:
                    self.log.info("├╼[initcriteria] no criteria defined")

                while blocking_initcriteria > 0:
                    for initcriteria in _component.initcriteria:
                        if initcriteria.is_alive():
                            time.sleep(0.005)
                            continue
                        else:
                            if initcriteria.ok is True:
                                self.log.obsok("├╼[initcriteria] found '%s'" % initcriteria.criteria)
                            else:
                                self.log.obswar("├╼[initcriteria] missing '%s'" % initcriteria.criteria)
                                if _component.initpolicy == 'strict':
                                    self.log.obserr("└╼[initcriteria] strict init policy enabled in config for '%s'" % component_name)
                                    self.strict_policy_missed = True
                                    self.lock.release()
                                    return
                            blocking_initcriteria -= 1
                            _component.initcriteria.remove(initcriteria)
                            self.log.debug("├╼[initcriteria] waiting for %d criteria" % blocking_initcriteria)
                # Release the global lock
                self.lock.release()
                self.log.info("└╼[initcriteria] done")

            else:
                self.log.debug("[launcher] skipping '%s' on %s --> duplicate in components/groups?" % (component_name, self.local_hostname))

    def deploy_commands(self):
        executed_list_components = {}
        executed_list_groups = {}
        for item in self.system_instance.flat_execution_list:
            if self.strict_policy_missed is False and self.exit_allowed_missed is False:
                if 'component' in item.keys():
                    _type = 'component'
                    component = item['component']
                    self.inner_deploy(component, executed_list_components, _type)
                if 'group' in item.keys():
                    _type = 'group'
                    group_name = item['group'].name
                    if group_name not in executed_list_groups.keys():
                        executed_list_groups[group_name] = "started"
                        self.log.info("┋[group] descending into '%s'" % item['group'].name)
                        for component in item['group'].flat_execution_list:
                            self.inner_deploy(component, executed_list_components, _type)
                    else:
                        self.log.debug(
                            "[launcher] skipping '%s' on %s --> duplicate in components/groups ?" % (item['group'].name, self.local_hostname))
            else:
                pass

    def construct_command(self, _host, _platform, _cmd, _component, _requires_x=None, _requires_remote_x=None):
        if _platform != self.local_platform:
            self.log.debug("[launcher] skipping '%s' what, running %s component on %s?!?" % (_component,
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
