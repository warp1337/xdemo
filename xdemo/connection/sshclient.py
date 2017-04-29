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


class SSHConnectionPool:
    def __init__(self, _log):
        self.log = _log
        self.client_pool = {}
        self.channel_pool = {}

    def add_client_to_pool(self, _hostname):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(_hostname, compress=True)
        transport = client.get_transport()
        channel = transport.open_session()
        if _hostname in self.channel_pool.keys():
            self.log.warning("[ssh] host %s already in connection pool" % _hostname)
        else:
            self.channel_pool[_hostname] = channel
            self.client_pool[_hostname] = client
        self.log.info("[ssh] connected to host %s" % _hostname)

    def close_all_connections(self):
        for _hostname in self.channel_pool.keys():
            self.log.info("[ssh] closing connection to host %s" % _hostname)
            if self.channel_pool[_hostname].send_ready():
                self.channel_pool[_hostname].send(chr(3))
            # self.channel_pool[_hostname].close()
            self.client_pool[_hostname].close()

    def close_single_connection(self, _hostname):
        if _hostname in self.channel_pool.keys():
            self.log.info("[ssh] closing connection to host %s" % _hostname)
            if self.channel_pool[_hostname].send_ready():
                self.channel_pool[_hostname].send(chr(3))
            # self.channel_pool[_hostname].close()
            self.client_pool[_hostname].close()
        else:
            self.log.warning("[ssh] host %s not in pool" % _hostname)

    def get_channel_connection(self, _hostname):
        if _hostname in self.channel_pool.keys():
            return self.channel_pool[_hostname]
        else:
            self.log.warning("[ssh] host %s not in channel pool" % _hostname)
            return None

    def get_client_connection(self, _hostname):
        if _hostname in self.client_pool.keys():
            return self.client_pool[_hostname]
        else:
            self.log.warning("[ssh] host %s not in client pool" % _hostname)
            return None

    def send_cmd_to_channel(self, _hostname, _cmd, _requires_x=False):
        channel = self.get_channel_connection(_hostname)
        if channel is not None:
            _cmd = "export DISPLAY=:0.0 && " + _cmd
            self.log.debug("[ssh] executing '%s' on host %s" % (_cmd, _hostname))
            channel.get_pty()
            channel.exec_command(_cmd)
        else:
            pass

    def send_cmd_to_client(self, _hostname, _cmd, _requires_x=False, _environment=None):
        client = self.get_client_connection(_hostname)
        if client is not None:
            _cmd = "export DISPLAY=:0.0 && " + _cmd
            self.log.debug("[ssh] executing '%s' on host %s" % (_cmd, _hostname))
            stdin, stdout, stderr = client.exec_command(_cmd,
                                                        bufsize=-1,
                                                        timeout=None,
                                                        get_pty=True,
                                                        environment=_environment)
        else:
            pass
