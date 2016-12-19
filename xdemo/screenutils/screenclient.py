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

# SCREEN UTILS
from xdemo.screenutils.screen import Screen, list_screens


class ScreenPool(object):
    def __init__(self, _log, _log_folder):
        self.log = _log
        self.s_sessions = {}
        self.log_folder = _log_folder

    def new_screen_session(self, _screen_name, _runtimeenvironment):
        uid = _screen_name
        s_session = Screen(uid, self.log)
        s_session.initialize(_runtimeenvironment)
        s_session.enable_logs(self.log_folder + uid + ".log")
        if _screen_name in self.s_sessions.keys():
            self.log.debug("[screen] %s exists --> duplicate in components/groups?" % _screen_name)
            return None
        else:
            self.s_sessions[uid] = s_session
            return s_session

    def check_exists_in_pool(self, _screen_name):
        if _screen_name in self.s_sessions.keys():
            return self.s_sessions[_screen_name]
        else:
            self.log.error("[screen] %s does not exist" % _screen_name)
            return None

    def get_screen_id(self, _screen_name):
        uid = _screen_name.strip()
        result = self.check_exists_in_pool(uid)
        if result is not None:
            return result.id
        else:
            self.log.error("[screen] %s does not exist" % uid)
            return None

    def get_screen_status(self, _screen_name):
        uid = _screen_name.strip()
        result = self.check_exists_in_pool(uid)
        if result is not None:
            return result.status
        else:
            self.log.error("[screen] %s does not exist" % uid)
            return None

    def get_screen_is_initialized(self, _screen_name):
        uid = _screen_name.strip()
        result = self.check_exists_in_pool(uid)
        if result is not None:
            return result.exists
        else:
            self.log.error("[screen] %s does not exist" % uid)
            return None

    def get_screen_logfile(self, _screen_name):
        uid = _screen_name.strip()
        result = self.check_exists_in_pool(uid)
        if result is not None:
            return result._logfilename
        else:
            self.log.error("[screen] %s does not exist" % uid)
            return None

    def kill_screen(self, _screen_name):
        uid = _screen_name.strip()
        result = self.check_exists_in_pool(uid)
        if result is not None:
            result.kill()
            self.log.info("[screen] terminated %s" % uid)
        else:
            self.log.error("[screen] %s does not exist" % uid)
            return None

    def kill_all_screen_sessions(self):
        for name in self.s_sessions.keys():
            self.s_sessions[name].kill()
            self.log.info("[screen] %s terminated" % name)

    def send_cmd(self, _screen_name, _cmd, _type, _component_name):
        uid = _screen_name.strip()
        result = self.check_exists_in_pool(uid)
        if result is not None:
            result.send_commands(_cmd)
            if _type == 'component':
                self.log.info("[cmd] started '%s'" % _component_name)
            else:
                self.log.info("o---[cmd] started '%s'" % _component_name)
        else:
            self.log.error("[screen] %s does not exist" % uid)
            return None

    def list_all_screens(self):
        screen_list = []
        for name in self.s_sessions.keys():
            screen_list.append(name)
        return screen_list

    @staticmethod
    def list_all_screens_native():
        return list_screens()
