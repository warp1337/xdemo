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

import os
import sys
import yaml


class SystemConfig:

    def __init__(self, _configfile, _logger):
        self.groups = {}
        self.log = _logger
        self.components = {}
        self.base_path = None
        self.cfg_instance = None

        self.cfg_file = str(_configfile).strip()

        self.get_system_base_path()
        self.load_system_cfg_file()
        self.load_system_entities()

    def get_system_base_path(self):
        tmp_path = os.path.dirname(os.path.abspath(self.cfg_file))
        if os.path.exists(tmp_path):
            self.base_path = tmp_path
        else:
            self.log.error("path does not exist %s", tmp_path)
            sys.exit(1)

    def load_system_cfg_file(self):
        if os.path.isfile(self.cfg_file):
            with open(self.cfg_file, 'r') as current_config:
                try:
                    self.cfg_instance = yaml.load(current_config)
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("config file does not exist %s", self.cfg_file)
            sys.exit(1)

    def print_system_cfg_file(self):
        print self.cfg_instance

    def load_system_component_config(self, _config):
        current_config = self.base_path + ("/components/") + _config + ".yaml"
        if os.path.isfile(current_config):
            with open(current_config, 'r') as component_config:
                try:
                    self.components["_config"] = yaml.load(component_config)
                    print self.components["_config"]
                except yaml.YAMLError as e:
                    self.log.error(e)
                    sys.exit(1)
        else:
            self.log.error("config file does not exist %s", current_config)
            sys.exit(1)

    def load_system_group_config(self, _config):
        pass

    def load_system_entities(self):
        if 'xdemosystem' in self.cfg_instance[0].keys():
            if 'executionorder' in self.cfg_instance[0]['xdemosystem'].keys():
                for item in self.cfg_instance[0]['xdemosystem']['executionorder']:
                    if "component_" in item:
                        self.load_system_component_config(str(item))
                    elif "group_" in item:
                        self.load_system_group_config(str(item))
                    else:
                        self.log.error("group or component name is not valid %s" % item)
                        sys.exit(1)
            else:
                self.log.error("config file does not exist contain entry executionorder")
                sys.exit(1)
        else:
            self.log.error("config file does not exist contain entry xdemosystem")
            sys.exit(1)