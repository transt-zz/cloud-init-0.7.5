# vi: ts=4 expandtab
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3, as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from cloudinit.distros.parsers.resolv_conf import ResolvConf

from cloudinit import log as logging
from cloudinit import util

LOG = logging.getLogger(__name__)

# Translate Linux ethernet device name ie. eth0 to AIX form ie. en0
def translate_devname(devname):
    device = re.compile('eth[0-9]+')
    if device.match(devname):
        return devname.replace('th', 'n')
    else:
        return devname

# Call chdev to add route
def add_route(route):
    # First, delete the route if it exists on the system
    del_route(route)

    # Add the route if there isn't already a default route
    if get_route() is None:
        cmd = ['chdev', '-l', 'inet0']
        cmd.append("-aroute=" + "\"net,-hopcount,0,,0," + route + "\"")
        util.subp(cmd, capture=False)

# Call chdev to delete default route
def del_route(route):
    # if route exists, delete it
    if (route == get_route()):
        cmd = ['chdev', '-l', 'inet0']
        cmd.append("-adelroute=" + "\"net,-hopcount,0,,0," + route + "\"")
        util.subp(cmd, capture=False)

# Return the default route
def get_route():
    # First, delete the route
    cmd = ['lsattr', '-E', '-l', 'inet0', '-a', 'route', '-F', 'value']
    (out, err) = util.subp(cmd)
    if len(out):
        return out.split(",")[5]
    else:
        return None

