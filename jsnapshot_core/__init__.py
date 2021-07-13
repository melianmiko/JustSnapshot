from .btrfs_subvolume import BtrfsSubvolume
from .btrfs_volume import BtrfsVolume
from .fstab import FstabFile
from .initializer import initialize_app
from .callback import AppCallback, ConsoleColor
from .config import AppConfig, APP_DISK_MOUNT_POINT
from .engine import BackupEngine
from .snapshot import Snapshot
from . import os_patcher
import subprocess


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

