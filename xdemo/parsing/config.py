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
import sys
import yaml

# SELF
from xdemo.utilities.operatingsystem import is_file
from xdemo.utilities.operatingsystem import get_path_from_file
from xdemo.utilities.operatingsystem import get_file_from_path


class SystemConfig:
    def __init__(self, _configfile, _logger, _hostname, _platform, _localmode):
        # Basic definitions
        self.name = None
        self.groups = []
        self.log = _logger
        self.components = []
        self.base_path = None
        self.cfg_instance = None
        self.finishtrigger = None
        self.local_mode = _localmode
        self.executionduration = None
        self.flat_execution_list = []
        self.runtimeenvironment = None
        self.local_platform = _platform
        self.local_hostname = _hostname
        self.cfg_file = str(_configfile).strip()

        # Constructor functions to initialize the system data
        self.get_system_base_path()
        self.load_system_cfg_file()
        self.extract_base_data()
        self.load_system_entities()
        self.test_environment_files()

    # Helper function print the config
    def print_system_cfg_file(self):
        print self.cfg_instance

    # Extract the base path from given config file
    def get_system_base_path(self):
        tmp_path = get_path_from_file(self.cfg_file)
        if os.path.exists(tmp_path):
            self.base_path = tmp_path + "/"
        else:
            self.log.error("[config] path does not exist %s", tmp_path)
            sys.exit(1)

    # Get the base data for this system, like name, envionment, etc
    def extract_base_data(self):
        self.name = self.cfg_instance[0]['xdemosystem']['name'].strip()
        self.runtimeenvironment = self.cfg_instance[0]['xdemosystem']['runtimeenvironment']
        self.executionduration = self.cfg_instance[0]['xdemosystem']['executionduration']
        if 'finishtrigger' in self.cfg_instance[0]['xdemosystem']:
            self.finishtrigger = self.cfg_instance[0]['finishtrigger'].strip()

    # Check for convention of environment files
    def test_environment_files(self):
        if self.local_platform == 'posix' or self.local_platform == 'darwin':
            env_file = self.runtimeenvironment[self.local_platform].strip()
            target = self.base_path + env_file
            if is_file(target):
                self.log.debug("[config] using %s" % env_file)
                self.runtimeenvironment = target
            else:
                self.log.error("[config] env file %s not found" % target)
                sys.exit(1)

    # Check for convention of environment files
    def test_exec_file(self, _exec_file):
        if self.local_platform == 'posix' or self.local_platform == 'darwin':
            if is_file(_exec_file):
                pass
            else:
                self.log.error("[config] file %s not found" % _exec_file)
                self.log.error("[config] convention $[posix|darwin|win].$[sh|bat]")
                sys.exit(1)

    # Load and serialize the global system config yaml file
    def load_system_cfg_file(self):
        if os.path.isfile(self.cfg_file):
            with open(self.cfg_file, 'r') as current_config:
                try:
                    self.cfg_instance = yaml.load(current_config)
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("[config] file does not exist %s", self.cfg_file)
            sys.exit(1)

    # Extract all groups and components from config file
    def load_system_entities(self):
        exec_level = 0
        if 'xdemosystem' in self.cfg_instance[0].keys():
            if 'executionorder' in self.cfg_instance[0]['xdemosystem'].keys():
                for item in self.cfg_instance[0]['xdemosystem']['executionorder']:
                    no_folder_item = get_file_from_path(item)
                    if no_folder_item.startswith('component_'):
                        try:
                            tmp_item = item.split("@")
                            name = tmp_item[0].strip()
                            host = tmp_item[1].strip()
                        except Exception, e:
                            self.log.error("[config] no hostname provided? %s" % item)
                            sys.exit(1)
                        self.load_component_config(str(name), str(host), exec_level)
                        exec_level += 1
                        continue
                    elif item.startswith('group_'):
                        self.load_group_config(str(item.strip()), exec_level)
                        exec_level += 1
                        continue
                    else:
                        self.log.error("[config] group or component file name is not valid %s" % item)
                        sys.exit(1)
            else:
                self.log.error("[config] file does not exist contain entry 'executionorder'")
                sys.exit(1)
        else:
            self.log.error("[config] file does not exist contain entry 'xdemosystem'")
            sys.exit(1)

    # Get all components and their values from top level
    def load_component_config(self, _component, _host, _level, _in_group=False):
        current_config = self.base_path + ("/components/") + _component + ".yaml"
        if os.path.isfile(current_config):
            with open(current_config, 'r') as component_config:
                try:
                    tmp_component = yaml.load(component_config)
                    # Insert exec level
                    tmp_component[0]["level"] = _level

                    # DO NOT CHANGE THE NAMING PATTERN OR ALL HELL BREAKS LOSE
                    tmp_component[0]['xdemocomponent']["name"] = get_file_from_path(_component)
                    tmp_component[0]['xdemocomponent']["path"] = get_path_from_file(current_config)
                    # DO NOT CHANGE THE NAMING PATTERN OR ALL HELL BREAKS LOSE

                    path = tmp_component[0]['xdemocomponent']["path"]
                    platform = tmp_component[0]['xdemocomponent']["platform"].strip()

                    if platform == 'posix' or platform == 'darwin':
                        suffix = ".sh"
                        tmp_component[0]['xdemocomponent']["execscript"] = path + "/" + platform + suffix
                    else:
                        suffix = ".bat"
                        tmp_component[0]['xdemocomponent']["execscript"] = path + "/" + platform + suffix

                    self.test_exec_file(tmp_component[0]['xdemocomponent']["execscript"])

                    if self.local_mode is False:
                        tmp_component[0]['xdemocomponent']["executionhost"] = _host
                    else:
                        tmp_component[0]['xdemocomponent']["executionhost"] = self.local_hostname

                    if _in_group is False:
                        self.components.append(tmp_component)
                        self.flat_execution_list.append(tmp_component)
                    return tmp_component
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("[config] file %s does not exist", current_config)
            sys.exit(1)

    # Get all groups and included components
    def load_group_config(self, _group, _level):
        current_config = self.base_path + ("/groups/") + _group + ".yaml"
        if os.path.isfile(current_config):
            with open(current_config, 'r') as group_config:
                try:
                    tmp_group = yaml.load(group_config)
                    # Insert execution level
                    tmp_group[0]["level"] = _level
                    # Insert group name, already stripped
                    tmp_group[0]['xdemogroup']['name'] = _group
                    tmp_group[0]['xdemogroup']["flat_execution_list"] = []
                    sublevel = 0
                    for item in tmp_group[0]['xdemogroup']['components']:
                        if item.startswith('group_'):
                            self.log.error("[config] %s nested groups are not allowed" % _group)
                            sys.exit(1)
                        try:
                            tmp_item = item.split("@")
                            name = tmp_item[0].strip()
                            host = tmp_item[1].strip()
                        except Exception, e:
                            self.log.error("[config] no hostname provided? %s" % item)
                            sys.exit(1)
                        tmp_group[0]['xdemogroup']["flat_execution_list"].append(self.load_component_config(name, 
                                                                                                            host, 
                                                                                                            sublevel, 
                                                                                                            True))
                        sublevel += 1
                    self.groups.append(tmp_group)
                    self.flat_execution_list.append(tmp_group)
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("[config] file does not exist %s", current_config)
            sys.exit(1)
