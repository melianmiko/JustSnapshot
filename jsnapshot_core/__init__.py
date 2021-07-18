import subprocess

from .btrfs_volume import BtrfsVolume
from .config import APP_DISK_MOUNT_POINT


def find_devices():
    result = subprocess.run(["mount"], stdout=subprocess.PIPE)
    assert result.returncode == 0

    points = str(result.stdout, "utf8").split("\n")
    disks = []
    for a in points:
        if "btrfs" in a:
            device = a.split(" ")[0]
            if device not in disks:
                disks.append(device)

    return disks


def bind_root():
    return bind_volume(APP_DISK_MOUNT_POINT)


def bind_volume(path):
    return BtrfsVolume(path)

