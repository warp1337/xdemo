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

This file was part of: https://github.com/Christophe31/screenutils
and has been altered by the author. Thanks for this great Screen class!

"""

# STD
import os
import sys
try:
    from commands import getoutput
except:
    from subprocess import getoutput
from os import system
from time import sleep
from os.path import getsize
from threading import Thread

# SELF
from xdemo.utilities.operatingsystem import is_file
from xdemo.screenutils.errors import ScreenNotFoundError
from xdemo.utilities.operatingsystem import get_operating_system


def tailf(file_):
    """Each value is content added to the log file since last value return"""
    last_size = getsize(file_)
    while True:
        cur_size = getsize(file_)
        if (cur_size != last_size):
            f = open(file_, 'r')
            f.seek(last_size if cur_size > last_size else 0)
            text = f.read()
            f.close()
            last_size = cur_size
            yield text
        else:
            yield ""


def list_screens():
    """List all the existing screens and build a Screen instance for each
    """
    list_cmd = "screen -ls"
    return [
                Screen(".".join(l.split(".")[1:]).split("\t")[0])
                for l in getoutput(list_cmd).split('\n')
                if "\t" in l and ".".join(l.split(".")[1:]).split("\t")[0]
            ]


class Screen(object):
    """Represents a gnu-screen object::

        >>> s=Screen("screenName", initialize=True)
        >>> s.name
        'screenName'
        >>> s.exists
        True
        >>> s.state
        >>> s.send_commands("man -k keyboard")
        >>> s.kill()
        >>> s.exists
        False
    """

    def __init__(self, name, _info_dict, log):
        self.name = name
        self.log = log
        self._id = None
        self._status = None
        self.logs = None
        self._logfilename = None
        self.info_dict = _info_dict
        self.os_system = get_operating_system()
        self.runtimeenvironment = None

    @property
    def id(self):
        """return the identifier of the screen as string"""
        if not self._id:
            self._set_screen_infos()
        return self._id

    @property
    def status(self):
        """return the status of the screen as string"""
        self._set_screen_infos()
        return self._status

    @property
    def exists(self):
        """Tell if the screen session exists or not."""
        # Parse the screen -ls call, to find if the screen exists or not.
        #  "	28062.G.Terminal	(Detached)"
        lines = getoutput("screen -ls").split('\n')
        if self.name in [".".join(l.split(".")[1:]).split("\t")[0] for l in lines if self.name in l]:
            return self.name
        else:
            return None

    def enable_logs(self, filename=None):
        if filename is None:
            filename = self.name
        self._screen_commands("logfile " + filename, "log on ")
        self._screen_commands("logfile flush 0")
        self._logfilename = filename
        open(filename, 'w+')
        self.logs = tailf(filename)

    def disable_logs(self, remove_logfile=False):
        self._screen_commands("log off")
        if remove_logfile:
            system('rm ' + self._logfilename)
        self.logs = None

    def initialize(self, _environment=None):
        """initialize a screen, if does not exists yet"""
        if _environment is None:
            self.log.error("[screen] no environment file provided")
            sys.exit(1)

        # Double check existence
        if is_file(_environment):
            pass
        else:
            self.log.error("[screen] file not found %s" % _environment)
            sys.exit(1)

        self.runtimeenvironment = _environment

        if not self.exists:
            self._id = None
            # Detach the screen once attached, on a new tread.
            # Thread(target=self._delayed_detach).start()
            # Detach immediately
            # support Unicode (-U),
            # attach to a new/existing named screen (-R).
            self.log.info("[screen] session in env %s" % os.path.basename(self.runtimeenvironment))
            source_cmd = ". %s && " % self.runtimeenvironment
            system(source_cmd + 'stdbuf -oL' + ' screen -U  -dmS ' + self.name)

    def interrupt(self):
        """Insert CTRL+C in the screen session"""
        self._screen_commands("eval \"stuff \\003\"")

    def kill(self):
        """Kill the screen applications then close the screen"""
        self._screen_commands('quit')

    def detach(self):
        """detach the screen"""
        self._check_exists()
        system("screen -d " + self.id)

    def send_commands(self, *commands):
        """send commands to the active gnu-screen"""
        self._check_exists()
        for command in commands:
            self._screen_commands('stuff "' + command + '" ',
                                  'eval "stuff \\015"')

    def add_user_access(self, unix_user_name):
        """allow to share your session with an other unix user"""
        self._screen_commands('multiuser on', 'acladd ' + unix_user_name)

    def _screen_commands(self, *commands):
        """allow to insert generic screen specific commands
        a glossary of the existing screen command in `man screen`"""
        self._check_exists()
        for command in commands:
            # Runtime Environment has been set in the initialize step
            final_cmd = 'screen -x ' + self.id + ' -X ' + command
            system(final_cmd)
            sleep(0.05)

    def clean_log(self):
        clean_log = "echo '' > %s" % self._logfilename.strip()
        system(clean_log)

    def _check_exists(self, message="Error code: 404."):
        """check whereas the screen exist. if not, raise an exception"""
        session = self.exists
        if session is not None:
            pass
            # raise ScreenNotFoundError(message, self.name)
        else:
            self.log.error("[screen] '%s' does not exists" % session)

    def _set_screen_infos(self):
        """set the screen information related parameters"""
        if self.exists:
            line = ""
            for l in getoutput("screen -ls").split("\n"):
                if (
                        self.name in l and
                        self.name == ".".join(
                            l.split('\t')[1].split('.')[1:]) in l):
                    line = l
            if not line:
                # raise ScreenNotFoundError("While getting info.", self.name)
                self.log.error("[screen] '%s' could not get info", self.name)
            infos = line.split('\t')[1:]
            self._id = infos[0].split('.')[0]
            if len(infos) == 3:
                self._date = infos[1][1:-1]
                self._status = infos[2][1:-1]
            else:
                self._status = infos[1][1:-1]

    def _delayed_detach(self):
        sleep(0.1)
        self.detach()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)
