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


class SystemConfig:
    def __init__(self, _configfile, _logger, _hostname, _platform):
        self.name = None
        self.groups = []
        self.log = _logger
        self.components = []
        self.base_path = None
        self.cfg_instance = None
        self.finishtrigger = None
        self.executionduration = None
        self.flat_execution_list = []
        self.runtimeenvironment = None
        self.local_platform = _platform
        self.local_hostname = _hostname
        self.cfg_file = str(_configfile).strip()

        # Constructor functions to get the system data
        self.get_system_base_path()
        self.load_system_cfg_file()
        self.load_system_entities()
        self.extract_base_data()
        self.test_environment_files()

    # Helper function print the config
    def print_system_cfg_file(self):
        print self.cfg_instance

    # Get the base data for this system, like name, envionment, etc
    def extract_base_data(self):
        self.name = self.cfg_instance[0]['xdemosystem']['name'].strip()
        self.runtimeenvironment = self.cfg_instance[0]['xdemosystem']['runtimeenvironment']
        self.executionduration = self.cfg_instance[0]['xdemosystem']['executionduration']
        if 'finishtrigger' in self.cfg_instance[0]['xdemosystem']:
            self.finishtrigger = self.cfg_instance['finishtrigger'].strip()

    # Extract the base path from given config file
    def get_system_base_path(self):
        tmp_path = os.path.dirname(os.path.abspath(self.cfg_file))
        if os.path.exists(tmp_path):
            self.base_path = tmp_path + "/"
        else:
            self.log.error("[config] path does not exist %s", tmp_path)
            sys.exit(1)

    # Check for convention of environment files
    def test_environment_files(self):
        if self.local_platform == 'posix':
            env_file = self.runtimeenvironment[self.local_platform].strip()
            target = self.base_path + env_file
            if is_file(target):
                self.log.debug("[config] using %s" % env_file)
                self.runtimeenvironment = target
            else:
                self.log.error("[config] env file %s not found" % target)
                sys.exit(1)

    # Load and serialize the global system config file
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

    # Get all components and their values
    def load_system_component_config(self, _component, _level):
        current_config = self.base_path + ("/components/") + _component.strip() + ".yaml"
        if os.path.isfile(current_config):
            with open(current_config, 'r') as component_config:
                try:
                    tmp_component = yaml.load(component_config)
                    tmp_component[0]["level"] = _level
                    self.components.append(tmp_component)
                    self.flat_execution_list.append(tmp_component)
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("[config] file does not exist %s", current_config)
            sys.exit(1)

    # Get all components and their values
    def extract_component_config(self, _component, _level):
        current_config = self.base_path + ("/components/") + _component.strip() + ".yaml"
        if os.path.isfile(current_config):
            with open(current_config, 'r') as component_config:
                try:
                    actual_component_config = yaml.load(component_config)
                    actual_component_config[0]["sublevel"] = _level
                    return actual_component_config
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("[config] file does not exist %s", current_config)
            sys.exit(1)

    # Get all groups and included components
    def load_system_group_config(self, _group, _level):
        current_config = self.base_path + ("/groups/") + _group.strip() + ".yaml"
        if os.path.isfile(current_config):
            with open(current_config, 'r') as group_config:
                try:
                    tmp_group = yaml.load(group_config)
                    tmp_group[0]["level"] = _level
                    tmp_group[0]['xdemogroup']["flat_execution_list"] = []
                    sublevel = 0
                    for item in tmp_group[0]['xdemogroup']['components']:
                        tmp_group[0]['xdemogroup']["flat_execution_list"].append(
                            self.extract_component_config(str(item), sublevel))
                        sublevel += 1
                    self.groups.append(tmp_group)
                    self.flat_execution_list.append(tmp_group)
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("[config] file does not exist %s", current_config)
            sys.exit(1)

    # Extract all groups and components from config file
    def load_system_entities(self):
        exec_level = 0
        if 'xdemosystem' in self.cfg_instance[0].keys():
            if 'executionorder' in self.cfg_instance[0]['xdemosystem'].keys():
                for item in self.cfg_instance[0]['xdemosystem']['executionorder']:
                    if "component_" in item:
                        self.load_system_component_config(str(item), exec_level)
                        exec_level += 1
                        continue
                    elif "group_" in item:
                        self.load_system_group_config(str(item), exec_level)
                        exec_level += 1
                        continue
                    else:
                        self.log.error("[config] group or component name is not valid %s" % item)
                        sys.exit(1)
            else:
                self.log.error("[config] file does not exist contain entry executionorder")
                sys.exit(1)
        else:
            self.log.error("[config] file does not exist contain entry xdemosystem")
            sys.exit(1)

    # If level is debug, print some info
    def debug_info(self):
        self.log.debug("[config] system base data")
        self.log.debug(
            "[config] name: %s, runtimeenvironment: %s executionduration: %s, finsishtrigger: %s" % (self.name,
                                                                                                     self.runtimeenvironment,
                                                                                                     self.executionduration,
                                                                                                     self.finishtrigger))
