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

import paramiko


class ConnectionPool:

    def __init__(self, _log):
        self.pool = {}
        self.log = _log

    def add_client_to_pool(self, _hostname):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(_hostname, compress=True)
        if _hostname in self.pool.keys():
            self.log.warning("[%s] already in connection pool" % _hostname)
        else:
            self.pool[_hostname] = client

    def close_all_connections(self):
        for host in self.pool.keys():
            self.pool[host].close()

    def __get_connetion(self, _hostname):
        if _hostname in self.pool.keys():
            return self.pool[_hostname]
        else:
            self.log.warning("[%s] not in pool" % _hostname)
            return None

    def send_cmd_to_connection(self, _hostname, _cmd, _requires_x=False):
            client = self.__get_connetion(_hostname)
            if client is not None:
                if _requires_x is True:
                    _cmd = "export DISPLAY=:0.0 && " + _cmd
                self.log.info("executing command: %s" % _cmd)
                stdin, stdout, stderr = client.exec_command(_cmd)
                for line in stdout.read().splitlines():
                    print line

                for line in stderr.read().splitlines():
                    print line
            else:
                self.log.warning("[%s] connection not active" % _hostname)

