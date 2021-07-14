import os

import jsnapshot_core


def patch_fstab_of_backup(restored_volumes, callback, config):
    """
    Find and patch fstab in restored subvolumes.

    :param restored_volumes: List of restored subvolumes
    :param callback: User callback class
    :param config: App config obj
    :return: nothing
    """
    fstab_file = ""
    for a in restored_volumes:
        if os.path.isfile(a.get_absolute_path() + "/etc/fstab"):
            fstab_file = a.get_absolute_path() + "/etc/fstab"

    if not fstab_file:
        callback.warn("Fstab not found...")
        return

    callback.notice("Patching fstab file: " + fstab_file)
    fstab = jsnapshot_core.FstabFile(fstab_file)
    for line in fstab.records:
        if line.device != config.target_device:
            continue
        if "subvolid" not in line.flags or "subvol" not in line.flags:
            continue

        subvolume_name = line.flags["subvol"]
        new_id = -1
        for a in restored_volumes:
            if a.path == subvolume_name:
                new_id = a.id

        if new_id < 0:
            continue

        line.id = new_id
        callback.notice("Replaced ID in fstab row with subvolume " + subvolume_name)

    fstab.save()
    callback.notice("Fstab saved")

