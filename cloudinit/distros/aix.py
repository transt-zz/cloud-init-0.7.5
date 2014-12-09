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

from cloudinit import distros
from cloudinit import helpers
from cloudinit import log as logging
from cloudinit import util

from cloudinit.distros import net_util
from cloudinit.distros import rhel_util
from cloudinit.distros import aix_util
from cloudinit.settings import PER_INSTANCE

from cloudinit.distros.parsers.hostname import HostnameConf

LOG = logging.getLogger(__name__)

class Distro(distros.Distro):
    hostname_conf_fn = "/etc/hosts"
    resolve_conf_fn = "/etc/resolv.conf"

    def __init__(self, name, cfg, paths):
        distros.Distro.__init__(self, name, cfg, paths)
        # This will be used to restrict certain
        # calls from repeatly happening (when they
        # should only happen say once per instance...)
        self._runner = helpers.Runners(paths)
        self.osfamily = 'aix'

    def install_packages(self, pkglist):
        self.package_command('install', pkgs=pkglist)

    def apply_network(self, settings, bring_up=True):
        # Write it out
        dev_names = _write_network(settings)
        # Now try to bring them up
        if bring_up:
            return _bring_up_interfaces(dev_names)
        return False

    def _write_network(self, settings):
        entries = net_util.translate_network(settings)
        print("Translated ubuntu style network settings %s into %s" % (settings, entries))
        # Make the intermediate format as the rhel format...
        nameservers = []
        searchservers = []
        dev_names = entries.keys()

        chdev_cmd = ['chdev']
        log_chdev_cmd = ['chdev']
        chdev_opts = {
                "address" : '-anetaddr=',
                "netmask" : '-anetmask=',
        }

        for (dev, info) in entries.iteritems():
            if dev not in 'lo':
                chdev_cmd.extend(['-l', translate_devname(dev)])
                log_chdev_cmd.extend(['-l', translate_devname(dev)])
                for (key, val) in info.iteritems():
                    if key in chdev_opts and val and isinstance(val, basestring):
                        chdev_cmd.append(chdev_opts[key] + val)
                        log_chdev_cmd.append(chdev_opts[key] + val)
                chdev_cmd.append("-astate=down")
                log_chdev_cmd.append("-astate=down")

                try:
                    subp(chdev_cmd, logstring=log_chdev_cmd)
                except Exception as e:
                    raise e

                aix_util.add_route(info.get('gateway'))

            if 'dns-nameservers' in info:
                nameservers.extend(info['dns-nameservers'])
            if 'dns-search' in info:
                searchservers.extend(info['dns-search'])

        if nameservers or searchservers:
            rhel_util.update_resolve_conf_file(resolve_conf_fn, nameservers, searchservers)
        return dev_names

    def apply_locale(self, locale, out_fn=None):
        util.subp(['chlang', '-m', str(locale)])

    def _write_hostname(self, hostname, out_fn):
        # Permanently change the hostname for inet0 device in the ODM
        util.subp(['chdev', '-l', 'inet0', '-a', 'hostname=' + str(hostname)])

        # Change the node for the uname process
        util.subp(['uname', '-S', str(hostname)])

        # Change the hostname on the current running system
        util.subp(['hostname', str(hostname)])

    def _select_hostname(self, hostname, fqdn):
        # Should be fqdn if we can use it
        if fqdn:
            return fqdn
        return hostname

    def _read_system_hostname(self):
        host_fn = self.hostname_conf_fn
        return (host_fn, self._read_hostname(host_fn))

    def _read_hostname(self, filename, default=None):
        (out, _err) = util.subp(['hostname'])
        if len(out):
            return out
        else:
            return default

    def _bring_up_interface(self, device_name):
        if device_name in 'lo':
            return True

        cmd = ['chdev', '-l', translate_devname(device_name), '-a', 'state=up']
        LOG.debug("Attempting to run bring up interface %s using command %s", device_name, cmd)
        try:
            (_out, err) = util.subp(cmd)
            if len(err):
                LOG.warn("Running %s resulted in stderr output: %s", cmd, err)
            return True
        except util.ProcessExecutionError:
            util.logexc(LOG, "Running interface command %s failed", cmd)
            return False

    def _bring_up_interfaces(self, device_names):
        if device_names and 'all' in device_names:
            raise RuntimeError(('Distro %s can not translate the device name "all"') % (self.name))
        for d in device_names:
            if not self._bring_up_interface(d):
                return False
        return True

    def set_timezone(self, tz):
        cmd = ['chtz', tz]
        util.subp(cmd)

    def package_command(self, command, args=None, pkgs=None):
        if pkgs is None:
            pkgs = []

        cmd = ['yum']
        # If enabled, then yum will be tolerant of errors on the command line
        # with regard to packages.
        # For example: if you request to install foo, bar and baz and baz is
        # installed; yum won't error out complaining that baz is already
        # installed.
        cmd.append("-t")
        # Determines whether or not yum prompts for confirmation
        # of critical actions. We don't want to prompt...
        cmd.append("-y")

        if args and isinstance(args, str):
            cmd.append(args)
        elif args and isinstance(args, list):
            cmd.extend(args)

        cmd.append(command)

        pkglist = util.expand_package_list('%s-%s', pkgs)
        cmd.extend(pkglist)

        # Allow the output of this to flow outwards (ie not be captured)
        util.subp(cmd, capture=False)

    def update_package_sources(self):
        self._runner.run("update-sources", self.package_command,
                         ["makecache"], freq=PER_INSTANCE)

    def add_user(self, name, **kwargs):
        if util.is_user(name):
            LOG.info("User %s already exists, skipping.", name)
            return False

        adduser_cmd = ['useradd']
        log_adduser_cmd = ['useradd']

        adduser_opts = {
                "homedir": '-d',
                "gecos": '-c',
                "primary_group": '-g',
                "groups": '-G',
                "shell": '-s',
                "expiredate" : '-e',
        }

        redact_opts = ['passwd']

        for key, val in kwargs.iteritems():
            if key in adduser_opts and val and isinstance(val, basestring):
                adduser_cmd.extend([adduser_opts[key], val])

                # Redact certain fields from the logs
                if key in redact_opts:
                    log_adduser_cmd.extend([adduser_opts[key], 'REDACTED'])
                else:
                    log_adduser_cmd.extend([adduser_opts[key], val])

        if 'no_create_home' in kwargs or 'system' in kwargs:
            adduser_cmd.append('-d/nonexistent')
            log_adduser_cmd.append('-d/nonexistent')
        else:
            adduser_cmd.append('-m')
            adduser_cmd.append('-m')
            log_adduser_cmd.append('-m')
            log_adduser_cmd.append('-m')

        adduser_cmd.append(name)
        log_adduser_cmd.append(name)

        # Run the command
        LOG.debug("Adding user %s", name)
        try:
            util.subp(adduser_cmd, logstring=log_adduser_cmd)
        except Exception as e:
            util.logexc(LOG, "Failed to create user %s", name)
            raise e

    def create_user(self, name, **kwargs):
        """
        Creates users for the system using the GNU passwd tools. This
        will work on an GNU system. This should be overriden on
        distros where useradd is not desirable or not available.
        """
        # Add the user
        self.add_user(name, **kwargs)

        # Set password if plain-text password provided and non-empty
        if 'plain_text_passwd' in kwargs and kwargs['plain_text_passwd']:
            self.set_passwd(name, kwargs['plain_text_passwd'])

        # Default locking down the account.  'lock_passwd' defaults to True.
        # lock account unless lock_password is False.
        if kwargs.get('lock_passwd', True):
            self.lock_passwd(name)

        # Configure sudo access
        if 'sudo' in kwargs:
            self.write_sudo_rules(name, kwargs['sudo'])

        # Import SSH keys
        if 'ssh_authorized_keys' in kwargs:
            keys = set(kwargs['ssh_authorized_keys']) or []
            ssh_util.setup_user_keys(keys, name, options=None)
        return True

    def lock_passwd(self, name):
        """
        Lock the password of a user, i.e., disable password logins
        """
        try:
            # Need to use the short option name '-l' instead of '--lock'
            # (which would be more descriptive) since SLES 11 doesn't know
            # about long names.
            util.subp(['chuser', 'account_locked=true', name])
        except Exception as e:
            util.logexc(LOG, 'Failed to disable password for user %s', name)
            raise e

    def create_group(self, name, members):
        group_add_cmd = ['mkgroup', name]

        # Check if group exists, and then add it doesn't
        if util.is_group(name):
            LOG.warn("Skipping creation of existing group '%s'" % name)
        else:
            try:
                util.subp(group_add_cmd)
                LOG.info("Created new group %s" % name)
            except Exception:
                util.logexc("Failed to create group %s", name)

        # Add members to the group, if so defined
        if len(members) > 0:
            for member in members:
                if not util.is_user(member):
                    LOG.warn("Unable to add group member '%s' to group '%s'; user does not exist.", member, name)
                    continue

                util.subp(['usermod', '-G', name, member])
                LOG.info("Added user '%s' to group '%s'" % (member, name))
