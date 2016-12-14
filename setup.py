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
import subprocess
from setuptools import setup, find_packages

version = "master"
filename = "master"

setup(name="xdemo",

      version=filename,

      description="A generic and configurable software launcher",

      long_description="A generic and configurable software launcher",

      author="Florian Lier",

      author_email="flier[at]techfak.uni-bielefeld.de",

      url="https://github.com/warp1337/xdemo",

      download_url="https://github.com/warp1337/xdemo",

      packages=find_packages(exclude=["*.unittests", "*.unittests.*", "unittests.*", "unittests"]),

      scripts=[],

      package_data={'xdemo': ['examples/*']},

      include_package_data=True,

      keywords=['Test',
                'System Testing',
                'Component Based Testing',
                'Software Tests',
                'Automated System Execution'
                'Execution Engine',
                'Experiment Execution'],

      license="LGPLv3",

      classifiers=['Development Status :: Beta',
                   'Environment :: Console',
                   'Environment :: Robotics',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Library or ' +
                   'Lesser General Public License (LGPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Text Processing :: Markup :: XML'],

      install_requires=['fabric==1.13.1', 'pyyaml==3.12', 'colorlog'],

      # Workaround for: http://bugs.python.org/issue856103
      zip_safe=False

      )

# Make bin/scripts executable
if os.name.lower() == "linux":
    subprocess.call(["chmod -R ugo+x bin"], shell=True)
