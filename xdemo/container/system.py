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

import sys


class System:

    def __init__(self, _raw_flat_execution_list, _log):
        self.log = _log
        self.name = None
        self.groups = []
        self.components = []
        self.flat_executionlist = []
        self.runtimeenvironment = None
        self.executionduration = None
        self.raw_execution_list = _raw_flat_execution_list

        self.initialize()
        self.log.debug("instance flat executuion list")
        self.log.debug(self.flat_executionlist)
        self.log.debug("-----------------")

    def initialize(self):
        for item in self.raw_execution_list:
            if 'xdemocomponent' in item[0]:
                self.add_component(item)
            if 'xdemogroup' in item[0]:
                self.add_group(item)

    def add_component(self, _component_data):
        c = Component(self.log)
        c.initialize(_component_data)
        self.components.append(c)
        tmp_component = {"component": c}
        self.flat_executionlist.append(tmp_component)

    def add_group(self, _group_data):
        g = Group(self.log)
        g.initialize(_group_data)
        self.groups.append(g)
        tmp_group = {"group": g}
        self.flat_executionlist.append(tmp_group)


class Component:

    def __init__(self, _log):
        self.log = _log
        self.name = None
        self.level = None
        self.command = None
        self.observer = []
        self.autostart = None
        self.retrycount = None
        self.errorpolicy = None
        self.description = None
        self.executionhost = None
        self.blockexecution = None

    def initialize(self, _component_data):
        try:
            if 'level' in _component_data[0]:
                self.level = _component_data[0]['level']
            elif 'sublevel' in _component_data[0]:
                self.level = _component_data[0]['sublevel']
            self.name = _component_data[0]['xdemocomponent']['name']
            self.command = _component_data[0]['xdemocomponent']['command']
            self.observer = []
            self.autostart = _component_data[0]['xdemocomponent']['autostart']
            self.errorpolicy = _component_data[0]['xdemocomponent']['errorpolicy']
            self.description = _component_data[0]['xdemocomponent']['description']
            self.executionhost = _component_data[0]['xdemocomponent']['executionhost']
            self.blockexecution = _component_data[0]['xdemocomponent']['blockexecution']
        except Exception, e:
            self.log.error("key error in create component %s " % e)
            sys.exit(1)


class Group:

    def __init__(self, _log):
        self.log = _log
        self.name = None
        self.level = None
        self.autostart = None
        self.errorpolicy = None
        self.description = None
        self.blockexecution = None
        self.flat_execution_list = []

    def initialize(self, _group_data):
        try:
            self.level = _group_data[0]['level']
            self.name = _group_data[0]['xdemogroup']['name']
            self.autostart = _group_data[0]['xdemogroup']['autostart']
            self.errorpolicy = _group_data[0]['xdemogroup']['errorpolicy']
            self.description = _group_data[0]['xdemogroup']['description']
            self.blockexecution = _group_data[0]['xdemogroup']['blockexecution']
            for item in _group_data[0]['xdemogroup']['flat_execution_list']:
                c = Component(self.log)
                c.initialize(item)
                self.flat_execution_list.append(c)
        except Exception, e:
            self.log.error("key error in create group %s " % e)
            sys.exit(1)


class Observer:

    def __init__(self):
        self.type = None
        self.maxwaittime = None
        self.criteria = None
        self.retrycount = None
