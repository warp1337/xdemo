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


class SystemLauncherClient:
    def __init__(self, _system_instance, _screen_pool, _log):
        self.log = _log
        self.screen_pool = _screen_pool
        self.hierarchical_session_list = []
        self.hierarchical_component_list = []
        self.system_instance = _system_instance
        self.base_path = self.system_instance.base_path
        self.local_hostname = _system_instance.local_hostname
        self.local_platform = _system_instance.local_platform
        self.runtimeenvironment = _system_instance.runtimeenvironment

    def stop_all_observers(self):
        for item in self.hierarchical_component_list:
            values = item.values()
            for component in values:
                for obs in component.observer:
                     obs.keep_running = False

    def inner_mk_session(self, _component):
        component_host = _component.executionhost
        if component_host == self.local_hostname:
            # Name is actually derived from the path: component_something.yaml
            screen_name = _component.screen_id
            new_screen_session = self.screen_pool.new_screen_session(screen_name, self.runtimeenvironment)
            if new_screen_session is not None:
                informed_item = {screen_name: new_screen_session}
                self.hierarchical_session_list.append(informed_item)

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

    def inner_deploy(self, _component, _executed_list_components, _type):
        # Name is actually derived from the path: component_something.yaml
        component_name = _component.name
        cmd = _component.command
        platform = _component.platform
        host = _component.executionhost
        final_cmd = self.construct_command(host, platform, cmd, True, True)
        if final_cmd is None:
            return
        else:
            screen_name = _component.screen_id
            if screen_name not in _executed_list_components.keys():
                for observer in _component.observer:
                    observer.start()
                self.screen_pool.send_cmd(screen_name, final_cmd, _type, component_name)
                informed_item = {screen_name: _component}
                self.hierarchical_component_list.append(informed_item)
                _executed_list_components[screen_name] = "started"
                for observer in _component.observer:
                    now = time.time()
                    observer_result = False
                    if observer.type == 'stdoutobserver':
                        while time.time() - now <= observer.maxwaittime and observer_result is False:
                            observer_result = observer.ok
                        observer.stop()
                    if observer_result is True:
                        if _type == 'component':
                            self.log.info("    o---[observer] found '%s'" % observer.criteria)
                        else:
                            self.log.info("        o---[observer] found '%s'" % observer.criteria)
                    else:
                        if _type == 'component':
                            self.log.warning("    o---[observer] missed '%s'" % observer.criteria)
                        else:
                            self.log.warning("        o---[observer] missed '%s'" % observer.criteria)
            else:
                self.log.warning("[launcher] skipping '%s' on %s --> duplicate in components/groups?" %
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
                    self.log.info("[launcher] descending into '%s'" % item['group'].name)
                    for component in item['group'].flat_execution_list:
                        self.inner_deploy(component, executed_list_components, _type)
                else:
                    self.log.warning(
                        "[launcher] skipping '%s' on %s --> duplicate in components/groups?" %
                        (item['group'].name, self.local_hostname))

    def construct_command(self, _host, _platform, _cmd, _requires_x=None, _requires_remote_x=None):
        if _host == self.local_hostname and _platform == self.local_platform:
            return _cmd.strip()
        else:
            self.log.debug("[launcher] skipping %s | host %s | platform %s" % (_cmd, _host, _platform))
            return None
