#!/usr/bin/python2

from os import mkdir
from subprocess import check_output, CalledProcessError
from sys import argv

from os.path import isdir


# todo write json with already read data from phone in device directory,
# - save
# -- timestamp
# -- count
# load when device found, check if structure changed
# threads for time intensive operations
# arguments


def _help():
    print "usage: python", __file__, "[arguments]"
    print "\t-h\t--help"
    print "\t-a\t--apps"
    print "\t-m\t--media"
    print "\t-w\t--wifi\t\tneeds su enabled for adb"
    exit()


def parse_args():
    args = {
        "apps": False,
        "media": False,
        "wifi": False
    }

    i = 0
    while i < len(argv):
        if argv[i] in ["-h", "--help"]:
            _help()
        elif argv[i] in ["-a", "--apps"]:
            args["apps-only"] = True
        elif argv[i] in ["-m", "--media"]:
            args["media-only"] = True
        elif argv[i] in ["-w", "--wifi"]:
            args["wifi"] = True
        i += 1

    return args


def execute_cmd(cmd):
    if not isinstance(cmd, list):
        cmd = cmd.split(' ')
    print cmd
    try:
        return check_output(cmd)
    except CalledProcessError as e:
        print e.message
        pass


def get_devices(o):
    devices = []
    o = o.split('\n')
    devices.append(o[1].split('\t')[0])
    return devices


def get_packages(o):
    packages = []
    o = o.split('\n')
    for p in o:
        p = p[8:]
        if not p.startswith("com.android") and not p.startswith("com.google") and "lineageos" not in p and p != '':
            packages.append(p)
    return packages


def get_apk_paths(device, apks):
    paths = []
    for apk in apks:
        paths.append(execute_cmd(["adb", "-s", device, "shell", "pm", "path", apk])[8:].strip('\n'))
    return paths


def backup_apks(device, paths):
    apk_dir = device + "/apk/"
    if not isdir(apk_dir):
        mkdir(apk_dir)
    for path in paths:
        path = path.split('/')[-1]
        execute_cmd(["adb", "-s", device, "pull", path, apk_dir + path])


def backup_wifi(device):
    if not isdir(device + "/wifi"):
        mkdir(device + "/wifi")
    execute_cmd(["adb", "root"])
    execute_cmd(["adb", "-s", device, "pull", "/data/misc/wifi/WifiConfigStore.xml",
                 device + "/wifi/WifiConfigStore.xml"])
    execute_cmd(["adb", "unroot"])


def backup_media(device):
    mkdir(device + "/media")
    execute_cmd(["adb", "-s", device, "pull", "/sdcard/.", device + "/media"])


def main():
    cfg = parse_args()
    execute_cmd("adb start-server")
    devices = get_devices(execute_cmd("adb devices"))
    for device in devices:
        if not isdir(device):
            mkdir(device)
        else:
            pass  # todo sync
        if cfg["apps"]:
            apks = get_packages(execute_cmd(["adb", "-s", device, "shell", "pm", "list", "packages"]))
            paths = get_apk_paths(device, apks)
            backup_apks(device, paths)
        if cfg["media"]:
            backup_media(device)
        if cfg["wifi"]:
            backup_wifi(device)


if __name__ == '__main__':
    main()
