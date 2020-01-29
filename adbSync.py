#!/usr/bin/python3

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


class Configuration(object):
    apps = False
    media = False
    wifi = False

    @staticmethod
    def help():
        print("usage: python", __file__, "[arguments]")
        print("\t-h\t--help")
        print("\t-a\t--apps")
        print("\t-m\t--media")
        print("\t-w\t--wifi\t\tneeds su enabled for adb")
        exit()

    @staticmethod
    def parse():
        cfg = Configuration()
        i = 0
        while i < len(argv):
            a = argv[i]
            if a in ["-h", "--help"]:
                Configuration.help()
            elif a in ["-a", "--apps"]:
                cfg.apps = True
            elif a in ["-m", "--media"]:
                cfg.media = True
            elif a in ["-w", "--wifi"]:
                cfg.wifi = True
            i += 1
        return cfg


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
        o = o.split('\n')
        for p in o:
            p = p[8:]
            if not p.startswith("com.android") and not p.startswith("com.google") and "lineageos" not in p and p != '':
                packages.append(p)
        return packages

    @staticmethod
    def get_apk_paths(device, apks):
        paths = []
        for apk in apks:
            paths.append(ADBWrapper.execute_cmd(["adb", "-s", device, "shell", "pm", "path", apk])[8:].strip(b'\n'))
        return paths

    @staticmethod
    def backup_apks(device, paths):
        apk_dir = device + "/apk/"
        if not isdir(apk_dir):
            mkdir(apk_dir)
        for path in paths:
            path = path.split('/')[-1]
            ADBWrapper.execute_cmd(["adb", "-s", device, "pull", path, apk_dir + path])

    @staticmethod
    def backup_wifi(device):
        if not isdir(device + "/wifi"):
            mkdir(device + "/wifi")
        ADBWrapper.execute_cmd(["adb", "root"])
        ADBWrapper.execute_cmd(["adb", "-s", device, "pull", "/data/misc/wifi/WifiConfigStore.xml",
                                device + "/wifi/WifiConfigStore.xml"])
        ADBWrapper.execute_cmd(["adb", "unroot"])

    @staticmethod
    def backup_media(device):
        mkdir(device + "/media")
        ADBWrapper.execute_cmd(["adb", "-s", device, "pull", "/sdcard/.", device + "/media"])

    @staticmethod
    def backup(cfg):
        ADBWrapper.execute_cmd("adb start-server")
        devices = ADBWrapper.get_devices(ADBWrapper.execute_cmd("adb devices"))
        for device in devices:
            if not isdir(device):
                mkdir(device)
            else:
                pass  # todo sync
            if cfg.apps:
                apks = ADBWrapper.get_packages(ADBWrapper.execute_cmd(["adb", "-s", device, "shell", "pm", "list",
                                                                       "packages"]))
                paths = ADBWrapper.get_apk_paths(device, apks)
                ADBWrapper.backup_apks(device, paths)
            if cfg.media:
                ADBWrapper.backup_media(device)
            if cfg.wifi:
                ADBWrapper.backup_wifi(device)


if __name__ == '__main__':
    ADBWrapper.backup(Configuration.parse())
