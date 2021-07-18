import os
import subprocess

from .fstab import FstabFile


def device_to_uuid(device):
    command = ["blkid", "-s", "UUID", "-o", "value", device]
    result = subprocess.run(command, stdout=subprocess.PIPE)

    return "UUID=" + str(result.stdout, "utf8").replace("\n", "")


def patch_fstab_of_backup(rootfs, restored_subvolumes, callback, config):
    """
    Find and patch fstab in restored subvolumes.

    :param rootfs: rootfs path
    :param restored_subvolumes: List of restored subvolumes
    :param callback: User callback class
    :param config: App config obj
    :return: nothing
    """
    fstab_file = rootfs + "/etc/fstab"

    if not os.path.isfile(fstab_file):
        callback.warn("Fstab not found in " + fstab_file)
        return

    callback.notice("Patching fstab file: " + fstab_file)
    fstab = FstabFile(fstab_file)
    target_device_names = [
        config.target_device,
        device_to_uuid(config.target_device)
    ]

    for line in fstab.records:
        if line.device not in target_device_names:
            continue
        if "subvolid" not in line.flags or "subvol" not in line.flags:
            continue

        subvolume_name = line.flags["subvol"]
        new_id = -1
        for a in restored_subvolumes:
            if a.path == subvolume_name or "/" + a.path == subvolume_name:
                new_id = a.id

        if new_id < 0:
            continue

        line.flags["subvolid"] = new_id
        callback.notice("Replaced ID in fstab row with subvolume " + subvolume_name + ": " + str(new_id))

    fstab.save()
    callback.notice("Fstab saved")

