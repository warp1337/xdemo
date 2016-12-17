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


class SystemLauncherClient:
    def __init__(self, _system_instance, _screen_pool, _log):
        self.log = _log
        self.screen_pool = _screen_pool
        self.hierarchical_session_list = []
        self.system_instance = _system_instance
        self.base_path = self.system_instance.base_path
        self.local_hostname = _system_instance.local_hostname
        self.local_platform = _system_instance.local_platform
        self.runtimeenvironment = _system_instance.runtimeenvironment

    def mk_screen_sessions(self):
        # Empty row before detach, simply looks good.
        print ""
        for item in self.system_instance.instance_flat_executionlist:
            if 'component' in item.keys():
                component_host = item['component'].executionhost
                if self.clean_str(component_host) == self.local_hostname:
                    name = item['component'].name.strip()
                    screen_name = self.mk_id("xdemo_component", name, self.local_hostname)
                    new_screen_session = self.screen_pool.new_screen_session(self.clean_str(screen_name),
                                                                             self.runtimeenvironment)
                    informed_item = {self.clean_str(screen_name): new_screen_session}
                    self.hierarchical_session_list.append(informed_item)

    def deploy_commands(self):
        for item in self.system_instance.instance_flat_executionlist:
            if 'component' in item.keys():
                name = item['component'].name.strip()
                cmd = item['component'].command
                platform = item['component'].platform
                host = item['component'].executionhost
                final_cmd = self.construct_command(host, platform, cmd, True, True)
                if final_cmd is None:
                    continue
                else:
                    screen_name = self.mk_id("xdemo_component", name, self.local_hostname)
                    self.screen_pool.send_cmd(screen_name, final_cmd)

    def construct_command(self, _host, _platform, _cmd, _requires_x=None, _requires_remote_x=None):
        if self.clean_str(_host) == self.local_hostname and self.clean_str(_platform) == self.local_platform:
            return _cmd.strip()
        else:
            self.log.debug("[launcher] skipping %s | host %s | platform %s" % (_cmd, _host, _platform))
            return None

    @staticmethod
    def clean_str(_input_string):
        return _input_string.strip().lower()

    def mk_id(self, _xdemo, _name, _host):
        return self.clean_str(_xdemo) + "_" + self.clean_str(_name) + "_" + self.clean_str(_host)
