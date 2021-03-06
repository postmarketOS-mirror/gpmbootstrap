import os
import re

import pmb
import subprocess
import logging
import glob


class ArgsSubstitute:
    def __init__(self):
        self.config = pmb.config.defaults["config"]
        config = pmb.config.load(self)
        self.aports = config.get("pmbootstrap", "aports")
        self.cache = {
            "apkbuild": {}
        }
        self.details_to_stdout = True
        self.verbose = False
        self.device = None


def init():
    configfile = pmb.config.defaults["config"]
    if not os.path.isfile(configfile):
        # Probably never ran pmbootstrap, init
        subprocess.run("yes '' | pmbootstrap -q --details-to-stdout init", shell=True)

    pmb.helpers.logging.init(ArgsSubstitute())


def get_vendors():
    args = ArgsSubstitute()
    vendors = sorted(pmb.helpers.devices.list_vendors(args))
    return vendors


def get_codenames(vendor):
    args = ArgsSubstitute()
    return sorted(pmb.helpers.devices.list_codenames(args, vendor))


def get_user_interfaces():
    args = ArgsSubstitute()
    return pmb.helpers.ui.list(args)


def get_timezones():
    zoneinfo_path = "/usr/share/zoneinfo/*"
    result = []
    for zone in glob.glob(zoneinfo_path):
        if os.path.isdir(zone):
            for subzone in glob.glob(zone + "/*"):
                result.append(subzone.replace("/usr/share/zoneinfo/", ""))
        else:
            result.append(zone.replace("/usr/share/zoneinfo/", ""))
    return sorted(result)


def get_device_info(codename):
    args = ArgsSubstitute()
    args.device = codename
    deviceinfo = pmb.parse.deviceinfo(args)
    return deviceinfo


def _pmbootstrap(command, inputs=None):
    regex = r"\*\*\* \((\d)/(\d)\) (.+) \*\*\*"

    p = subprocess.Popen(['pmbootstrap', '--details-to-stdout'] + command, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT, universal_newlines=True)
    if inputs:
        p.stdin.write(inputs)

    progress = 0
    status = ""
    for line in iter(p.stdout.readline, ''):
        m = re.search(regex, line)
        if m:
            a, b, status = m.groups()
            progress = (int(a) / int(b))
        yield progress, status, line


def config(codename, hostname, ssh, timezone, ui, user):
    list(_pmbootstrap(['config', 'device', codename]))
    list(_pmbootstrap(['config', 'hostname', hostname]))
    list(_pmbootstrap(['config', 'ssh_keys', str(ssh)]))
    list(_pmbootstrap(['config', 'timezone', timezone]))
    list(_pmbootstrap(['config', 'ui', ui]))
    list(_pmbootstrap(['config', 'user', user]))


def clean():
    list(_pmbootstrap(['-y', 'zap']))


def install(password, packages=None, sdcard=None):
    command = ['install']
    if sdcard:
        command += ['--sdcard', '/dev/' + sdcard]
    if packages is not None and len(packages) > 0:
        command += ['--add', ','.join(packages)]
    yield from _pmbootstrap(command, inputs="{p}\n{p}\n".format(p=password))


if __name__ == '__main__':
    get_device_info('pine64-pinephone')
