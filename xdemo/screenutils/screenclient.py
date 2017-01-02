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
from threading import Lock
from threading import Thread

# SCREEN UTILS
from xdemo.screenutils.screen import Screen, list_screens
from xdemo.utilities.operatingsystem import get_all_component_os_info, get_component_os_info, stop_all_components


class ScreenPool(Thread):
    def __init__(self, _log, _log_folder):
        Thread.__init__(self)
        self.log = _log
        self.lock = Lock()
        self.s_sessions = {}
        self.check_interval = 1.5
        self.keep_running = True
        self.log_folder = _log_folder
        self.hierarchical_session_list = []

    def new_screen_session(self, _screen_name, _runtimeenvironment, _info_dict):
        self.lock.acquire()
        s_session = Screen(_screen_name, _info_dict, self.log)
        s_session.initialize(_runtimeenvironment)
        s_session.enable_logs(self.log_folder + _screen_name + ".log")
        if _screen_name in self.s_sessions.keys():
            self.lock.release()
            self.log.debug("[pool] '%s' already exists --> duplicate in components/groups?" % _screen_name)
            return s_session
        else:
            self.s_sessions[_screen_name] = s_session
            self.hierarchical_session_list.append(_screen_name)
            self.lock.release()
            return s_session

    def check_exists_in_pool(self, _screen_name):
        self.lock.acquire()
        if _screen_name in self.s_sessions.keys():
            if self.__get_screen_status(_screen_name, self.s_sessions[_screen_name]) is not None:
                self.s_sessions[_screen_name].info_dict['screen_status'] = "ok"
                self.lock.release()
                return self.s_sessions[_screen_name]
            else:
                self.s_sessions[_screen_name].info_dict['screen_status'] = "gone"
                self.log.error("[pool] '%s' does not exist" % _screen_name)
                self.lock.release()
                return None
        else:
            self.lock.release()
            self.log.error("[pool] '%s' not in session list" % _screen_name)
            return None

    def get_screen_id(self, _screen_name):
        result = self.check_exists_in_pool(_screen_name.strip())
        self.lock.acquire()
        if result is not None:
            self.lock.release()
            return result.id
        else:
            self.lock.release()
            self.log.error("[pool] '%s' could not get screen id" % _screen_name.strip())
            return None

    def get_all_screen_ids(self):
        ids = []
        for key, value in self.s_sessions.iteritems():
            result = self.check_exists_in_pool(key.strip())
            self.lock.acquire()
            if result is not None:
                ids.append(result.id)
            else:
                self.log.error("[pool] '%s' id could not be read" % key)
                self.lock.release()
                return None
            self.lock.release()
        return ids

    def __get_screen_status(self, _screen_name, _session):
        if _session is not None:
            return _session.status
        else:
            self.log.error("[pool] '%s' status could not be fetched" % _screen_name.strip())
            return None

    def get_screen_is_initialized(self, _screen_name):
        result = self.check_exists_in_pool(_screen_name.strip())
        self.lock.acquire()
        if result is not None:
            self.lock.release()
            return result.exists
        else:
            self.lock.release()
            self.log.error("[pool] '%s' could read init status" % _screen_name.strip())
            return None

    def get_screen_logfile(self, _screen_name):
        result = self.check_exists_in_pool(_screen_name.strip())
        self.lock.acquire()
        if result is not None:
            self.lock.release()
            return result._logfilename
        else:
            self.lock.release()
            self.log.error("[pool] '%s' could not get log file" % _screen_name.strip())
            return None

    def kill_screen(self, _screen_name):
        result = self.check_exists_in_pool(_screen_name.strip())
        if result is not None:
            self.lock.acquire()
            result.kill()
            self.lock.release()
            self.log.info("[pool] '%s' terminated" % _screen_name.strip())
        else:
            self.log.error("[pool] '%s' could not be killed" % _screen_name.strip())
            return None

    def kill_all_screen_sessions(self):
        self.lock.acquire()
        for name in self.s_sessions.keys():
            self.s_sessions[name].kill()
            self.log.info("[pool] '%s' terminated" % name)
        self.lock.release()

    def send_cmd(self, _screen_name, _cmd, _type, _component_name):
        result = self.check_exists_in_pool(_screen_name.strip())
        if result is not None:
            self.lock.acquire()
            result.send_commands(_cmd)
            self.lock.release()
            if _type == 'component':
                self.log.info("[cmd] '%s' started" % _component_name)
            else:
                self.log.info("      [cmd] '%s' started" % _component_name)
            return 0
        else:
            self.log.error("[pool] '%s' command could not be sent" % _screen_name.strip())
            return None

    def clean_log(self, _screen_name):
        result = self.check_exists_in_pool(_screen_name.strip())
        if result is not None:
            self.lock.acquire()
            result.clean_log()
            self.lock.release()
        else:
            self.log.error("[pool] '%s' logs could not be cleaned" % _screen_name.strip())

    def list_all_screens(self):
        screen_list = []
        self.lock.acquire()
        for name in self.s_sessions.keys():
            screen_list.append(name)
        self.lock.release()
        return screen_list

    @staticmethod
    def list_all_screens_native():
        return list_screens()

    def get_session_os_info(self, _screen_name):
        session = self.check_exists_in_pool(_screen_name)
        self.lock.acquire()
        if session is None:
            self.lock.release()
            return -1
        else:
            status = get_component_os_info(self.log, session)
            self.lock.release()
            return status

    def update_all_session_os_info(self):
        self.lock.acquire()
        get_all_component_os_info(self.log, self.s_sessions)
        self.lock.release()

    def stop_all_components(self):
        self.lock.acquire()
        stop_all_components(self.log, self.s_sessions)
        self.lock.release()

    def stop_continuous_check(self):
        self.keep_running = False

    def run(self):
        last_checked = time.time()
        while self.keep_running:
            if time.time() - last_checked >= self.check_interval:
                last_checked = time.time()
                self.update_all_session_os_info()
            time.sleep(0.1)
