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
import uuid

# SELF
from xdemo.observer.stdout import StdoutObserver, StdoutExcludeObserver


class SystemInstance:
    def __init__(self, _systemconfig, _log, _log_folder):
        self.log = _log
        self.groups = []
        self.components = []
        self.uuid = str(uuid.uuid4())
        self.flat_execution_list = []
        self.log_folder = _log_folder
        self.name = str(_systemconfig.name)
        self.base_path = _systemconfig.base_path
        self.finishtrigger = _systemconfig.finishtrigger
        self.local_platform = _systemconfig.local_platform
        self.local_hostname = _systemconfig.local_hostname
        self.executionduration = _systemconfig.executionduration
        self.runtimeenvironment = _systemconfig.runtimeenvironment
        self.cfg_execution_list = _systemconfig.flat_execution_list

        self.initialize()

    def initialize(self):
        for item in self.cfg_execution_list:
            if 'xdemocomponent' in item[0]:
                self.add_component(item)
            if 'xdemogroup' in item[0]:
                self.add_group(item)

    def add_component(self, _component_data):
        c = Component(self.log, self.log_folder, self.local_hostname)
        c.initialize(_component_data)
        self.components.append(c)
        tmp_component = {"component": c}
        self.flat_execution_list.append(tmp_component)

    def add_group(self, _group_data):
        g = Group(self.log, self.log_folder, self.local_hostname)
        g.initialize(_group_data)
        self.groups.append(g)
        tmp_group = {"group": g}
        self.flat_execution_list.append(tmp_group)


class Component:
    def __init__(self, _log, _log_folder, _local_hostname):
        self.log = _log
        self.name = None
        self.level = None
        self.initcriteria = []
        self.command = None
        self.log_file = None
        self.platform = None
        self.screen_id = None
        self.autostart = None
        self.retrycount = None
        self.errorpolicy = None
        self.description = None
        self.executionhost = None
        self.uuid = str(uuid.uuid4())
        self.log_folder = _log_folder
        self.local_hostname = _local_hostname

    def initialize(self, _component_data):
        try:
            # a component may occur at 'top level' or can be a member of a group --> sublevel
            if 'level' in _component_data[0]:
                self.level = _component_data[0]['level']
            elif 'sublevel' in _component_data[0]:
                self.level = _component_data[0]['sublevel']
            self.name = _component_data[0]['xdemocomponent']['name']
            self.command = _component_data[0]['xdemocomponent']['command']
            self.platform = _component_data[0]['xdemocomponent']['platform']
            self.autostart = _component_data[0]['xdemocomponent']['autostart']
            self.errorpolicy = _component_data[0]['xdemocomponent']['errorpolicy']
            self.description = _component_data[0]['xdemocomponent']['description']
            self.executionhost = _component_data[0]['xdemocomponent']['executionhost']
            self.screen_id = self.mk_screen_id("xdemo", self.name, self.local_hostname)
            self.log_file = self.log_folder + self.mk_screen_id("xdemo", self.name, self.local_hostname) + ".log"
            if 'initcriteria' in _component_data[0]['xdemocomponent'].keys():
                for initcriteria in _component_data[0]['xdemocomponent']['initcriteria']:
                    if 'stdout' in initcriteria.keys():
                        obs = StdoutObserver(self.log_file, self.log, self.name,
                                             initcriteria['stdout']['criteria'],
                                             initcriteria['stdout']['maxwaittime'])
                        self.initcriteria.append(obs)
                    if 'stdoutexclude' in initcriteria.keys():
                        obs = StdoutExcludeObserver(self.log_file, self.log, self.name,
                                                    initcriteria['stdoutexclude']['criteria'],
                                                    initcriteria['stdoutexclude']['maxwaittime'])
                        self.initcriteria.append(obs)
        except Exception, e:
            self.log.error("key error in component '%s' %s " % (self.name, e))
            sys.exit(1)

    @staticmethod
    def mk_screen_id(_xdemo, _component_name, _host):
        return _xdemo + "_" + _component_name + "_" + _host


class Group:
    def __init__(self, _log, _log_folder, _local_hostname):
        self.log = _log
        self.name = None
        self.level = None
        self.autostart = None
        self.errorpolicy = None
        self.description = None
        self.log_folder = _log_folder
        self.flat_execution_list = []
        self.uuid = str(uuid.uuid4())
        self.local_hostname = _local_hostname

    def initialize(self, _group_data):
        try:
            self.level = _group_data[0]['level']
            self.name = _group_data[0]['xdemogroup']['name']
            self.autostart = _group_data[0]['xdemogroup']['autostart']
            self.errorpolicy = _group_data[0]['xdemogroup']['errorpolicy']
            self.description = _group_data[0]['xdemogroup']['description']
            for item in _group_data[0]['xdemogroup']['flat_execution_list']:
                c = Component(self.log, self.log_folder, self.local_hostname)
                c.initialize(item)
                self.flat_execution_list.append(c)
        except Exception, e:
            self.log.error("key error in group '%s' %s " % (self.name, e))
            sys.exit(1)
