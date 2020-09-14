#!/usr/bin/python3

from os import mkdir, listdir
from os.path import isdir

from subprocess import check_output, CalledProcessError

from argparse import ArgumentParser

# todo write json with already read data from phone in device directory,
# - save
# -- timestamp
# -- count
# load when device found, check if structure changed
# threads for time intensive operations


class ADBWrapper(object):
    @staticmethod
    def execute_cmd(cmd):
        if not isinstance(cmd, list):
            cmd = cmd.split(' ')
        print(cmd)
        try:
            return check_output(cmd)
        except CalledProcessError as e:
            print(e.stderr)
            pass

    @staticmethod
    def get_devices(o):
        devices = []
        o = o.split(b'\n')
        devices.append(o[1].split(b'\t')[0])
        return devices

    @staticmethod
    def get_packages(o):
        packages = []
        o = o.split(b'\n')
        for p in o:
            p = p[8:]
            if not p.startswith(b"com.android") and not p.startswith(b"com.google") and b"lineageos" not in p \
                    and p != b'':
                packages.append(p)
        return packages

    @classmethod
    def get_apk_paths(cls, device, apks):
        paths = []
        for apk in apks:
            paths.append(cls.execute_cmd(["adb", "-s", device, "shell", "pm", "path", apk])[8:].strip(b'\n'))
        return paths

    @classmethod
    def backup_apks(cls, device, paths):
        ap = device + b"/apk/"
        if not isdir(ap):
            mkdir(ap)
        for path in paths:
            dn = path.split(b'/')[-2].split(b'-')[0].split(b'.')[-1] + b".apk"
            p = path.split(b'/')[-1]
            cls.execute_cmd(["adb", "-s", device, "pull", path, ap + dn])

    @classmethod
    def backup_wifi(cls, device):
        wp = device + b"/wifi/"
        if not isdir(wp):
            mkdir(wp)
        cls.execute_cmd(["adb", "root"])
        cls.execute_cmd(["adb", "-s", device, "pull", "/data/misc/wifi/WifiConfigStore.xml",
                                wp + b"WifiConfigStore.xml"])
        cls.execute_cmd(["adb", "unroot"])

    @classmethod
    def backup_media(cls, device):
        mp = device + b"/media"
        mkdir(mp)
        cls.execute_cmd(["adb", "-s", device, "pull", "/sdcard/.", mp])

    @classmethod
    def backup(cls, a, device):
        if a.apps:
            apks = cls.get_packages(ADBWrapper.execute_cmd(["adb", "-s", device, "shell", "pm", "list",
                                                                   "packages"]))
            paths = cls.get_apk_paths(device, apks)
            cls.backup_apks(device, paths)
        if a.media:
            cls.backup_media(device)
        if a.wifi:
            cls.backup_wifi(device)

    @classmethod
    def sync_apps(cls, device):
        p = device + b"/apk/"
        if not isdir(device) or not isdir(p):
            return False
        for apk in listdir(p):
            cls.execute_cmd(["adb", "-s", device, "install", p + apk])
        return True

    @classmethod
    def sync_media(cls, device):
        p = device + b"/media/"
        if not isdir(device) or not isdir(p):
            return False
        cls.execute_cmd(["adb", "-s", device, "push", p + "*", "/sdcard/"])
        return True

    @classmethod
    def sync_wifi(cls, device):
        pass  # todo merge with current

    @classmethod
    def sync(cls, a, device):
        if a.apps:
            cls.sync_apps(device)
        if a.media:
            cls.sync_media(device)
        if a.wifi:
            cls.sync_wifi(device)

    @classmethod
    def main(cls):
        ap = ArgumentParser()
        ap.add_argument("-a", "--apps", help="backup/sync apps", action="store_true")
        ap.add_argument("-m", "--media", help="backup/sync media", action="store_true")
        ap.add_argument("-w", "--wifi", help="backup/sync wifi", action="store_true")
        ap.add_argument("-b", "--backup", help="backup", action="store_true")
        ap.add_argument("-s", "--sync", help="sync", action="store_true")
        a = ap.parse_args()

        if not a.backup and not a.sync:
            print("please specify if you would want to backup and/or sync your device(s)")
            ap.print_help()
            exit()

        cls.execute_cmd("adb start-server")
        devices = cls.get_devices(ADBWrapper.execute_cmd("adb devices"))
        for device in devices:
            if not isdir(device) and a.sync:
                print("the device '{0}' has not been backed up yet, so there is nothing to synchronize.")
                continue

            if not isdir(device):
                mkdir(device)

            if a.backup:
                cls.backup(a, device)
            if a.sync:
                cls.backup(a, device)
