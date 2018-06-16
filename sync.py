from os import mkdir
from subprocess import check_output, CalledProcessError

from os.path import isdir


# todo write json with already read data from phone in device directory,
# load when device found, check if structure changed
# threads for time intensive operations
# arguments


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


def backup_media(device):
    mkdir(device + "/media")
    execute_cmd(["adb", "-s", device, "pull", "/sdcard/.", device + "/media"])


def main():
    execute_cmd("adb start-server")
    devices = get_devices(execute_cmd("adb devices"))
    for device in devices:
        if not isdir(device):
            mkdir(device)
        else:
            pass  # todo sync
        apks = get_packages(execute_cmd(["adb", "-s", device, "shell", "pm", "list", "packages"]))
        paths = get_apk_paths(device, apks)
        backup_apks(device, paths)
        backup_media(device)


if __name__ == '__main__':
    main()
