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

import re
import contextlib

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
        cmd = ['/usr/sbin/chdev', '-l', 'inet0']
        cmd.append("-aroute=" + "\"net,-hopcount,0,,0," + route + "\"")
        util.subp(cmd, capture=False)

# Call chdev to delete default route
def del_route(route):
    # if route exists, delete it
    if (route == get_route()):
        cmd = ['/usr/sbin/chdev', '-l', 'inet0']
        cmd.append("-adelroute=" + "\"net,-hopcount,0,,0," + route + "\"")
        util.subp(cmd, capture=False)

# Return the default route
def get_route():
    # First, delete the route
    cmd = ['/usr/sbin/lsattr', '-E', '-l', 'inet0', '-a', 'route', '-F', 'value']
    (out, err) = util.subp(cmd)

    out = out.strip()
    if len(out):
        return out.split(",")[5]
    else:
        return None

# Return the device using the lsdev command output
def find_devs_with(path=None):
    """
    find devices matching given criteria (via lsdev)
    """
    lsdev_cmd = ['/usr/sbin/lsdev']
    options = []
    if path:
        options.append("-Cl")
        options.append(path)
    cmd = lsdev_cmd + options

    (out, _err) = util.subp(cmd)
    entries = []
    for line in out.splitlines():
        line = line.strip().split()[0]
        if line:
            entries.append(line)
    return entries

def mount_cb(device, callback, data=None, rw=False, mtype=None, sync=True):
    """
    Mount the device, call method 'callback' passing the directory
    in which it was mounted, then unmount.  Return whatever 'callback'
    returned.  If data != None, also pass data to callback.
    """
    mounted = mounts()
    with util.tempdir() as tmpd:
        umount = False
        devname="/dev/" + device
        if device in mounted:
            mountpoint = mounted[device]['mountpoint']
        elif devname in mounted:
            mountpoint = mounted[devname]['mountpoint']
        else:
            try:
                mountcmd = ['/usr/sbin/mount']
                mountopts = []
                if rw:
                    mountopts.append('rw')
                else:
                    mountopts.append('ro')
                if sync:
                    # This seems like the safe approach to do
                    # (ie where this is on by default)
                    mountopts.append("sync")
                if mountopts:
                    mountcmd.extend(["-o", ",".join(mountopts)])
                if mtype:
                    mountcmd.extend(['-t', mtype])

                if "/cd" in devname:
                        mountcmd.append('-vcdrfs')
                        mountcmd.append(devname)
                else:
                        mountcmd.append(device)

                mountcmd.append(tmpd)
                util.subp(mountcmd)
                umount = tmpd  # This forces it to be unmounted (when set)
                mountpoint = tmpd
            except (IOError, OSError) as exc:
                raise util.MountFailedError(("Failed mounting %s to %s due to: %s") % (device, tmpd, exc))
        # Be nice and ensure it ends with a slash
        if not mountpoint.endswith("/"):
            mountpoint += "/"

        with unmounter(umount):
            if data is None:
                ret = callback(mountpoint)
            else:
                ret = callback(mountpoint, data)
            return ret

def mounts():
    mounted = {}
    try:
        # Go through mounts to see what is already mounted
        (mountoutput, _err) = util.subp("/usr/sbin/mount")
        mount_locs = mountoutput.splitlines()
        mountre = r'\s+(/dev/[\S]+)\s+(/\S*)\s+(\S+)\s+(\S+ \d+ \d+:\d+) (\S+(,\S+)?)'
        for mpline in mount_locs:
            # AIX: /dev/hd4          524288    142672   73%    10402    38% /
            try:
                m = re.search(mountre, mpline)
                dev = m.group(1)
                mp = m.group(2)
                fstype = m.group(3)
                date = m.group(4)
                opts = m.group(5).split(",")[0]
            except:
                continue
            # If the name of the mount point contains spaces these
            # can be escaped as '\040', so undo that..
            mp = mp.replace("\\040", " ")
            mounted[dev] = {
                'fstype': fstype,
                'mountpoint': mp,
                'opts': opts,
                'date': date,
            }
        print("Fetched %s mounts" % mounted)
    except (IOError, OSError):
        print("Failed fetching mount points")
    return mounted

@contextlib.contextmanager
def unmounter(umount):
    try:
        yield umount
    finally:
        if umount:
            umount_cmd = ["/usr/sbin/umount", umount]
            util.subp(umount_cmd)

# Helper function to write the resolv.conf file
def write_resolv_conf_file(fn, r_conf):
    util.write_file(fn, str(r_conf), 0644)

# Helper function to write /etc/resolv.conf
def update_resolve_conf_file(fn, dns_servers, search_servers):
    try:
        r_conf = ResolvConf(util.load_file(fn))
        r_conf.parse()
    except IOError:
        util.logexc(LOG, "Failed at parsing %s reverting to an empty "
                    "instance", fn)
        r_conf = ResolvConf('')
        r_conf.parse()
    if dns_servers:
        for s in dns_servers:
            try:
                r_conf.add_nameserver(s)
            except ValueError:
                util.logexc(LOG, "Failed at adding nameserver %s", s)
    if search_servers:
        for s in search_servers:
            try:
                r_conf.add_search_domain(s)
            except ValueError:
                util.logexc(LOG, "Failed at adding search domain %s", s)
    write_resolv_conf_file(fn, r_conf)
