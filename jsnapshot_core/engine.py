import os.path

from datetime import datetime

from jsnapshot_core.config import AppConfig
from jsnapshot_core.os_patcher import patch_fstab_of_backup
from jsnapshot_core.snapshot import Snapshot, SNAPSHOT_NAME_FORMAT


class BackupEngine:
    def __init__(self, callback, volume):
        self.callback = callback
        self.volume = volume
        self.storage_path = self.volume.mount_point + "/_backups"

    def list_snapshots(self):
        """
        List all snapshots
        :return:
        """
        if not os.path.isdir(self.storage_path):
            return []

        out = []
        for name in os.listdir(self.storage_path):
            out.append(Snapshot(name, self.volume))

        out.sort(key=lambda x: x.get_date())

        return out

    def list_snapshots_with_tag(self, tag):
        """
        List all snapshots with specified tag
        :param tag: target tag
        :return: void
        """
        data = self.list_snapshots()
        out = []

        for a in data:
            if a.has_tag(tag):
                out.append(a)

        return out

    def restore_snapshot(self, target_snapshot, full=False, parts=None):
        """
        (DANGER) Restore snapshot
        :return: void
        """
        # Move current roots to new snapshot
        auto_snapshot = self._create_snapshot_item()
        config = AppConfig()
        self.callback.notice("Moving current system to new snapshot...")

        recover_paths = []
        for root in config.subvolumes:
            if not full and root not in parts:
                continue

            if os.path.isdir(self.volume.mount_point + "/" + root):
                vol = self.volume.get_subvolume(root)
                destination = auto_snapshot.path + "/" + vol.path
                self.callback.notice("Moving " + vol.path + " => " + destination)
                vol.move(destination)
                recover_paths.append({
                    "backup": vol.path,
                    "source": vol.original_path
                })

        auto_snapshot.metadata["subvolumes"] = recover_paths
        auto_snapshot.metadata["info"] = "Auto-snapshot before restoring: " + target_snapshot.name
        auto_snapshot.save_metadata()

        auto_snapshot.set_tag("fallback")

        # Recover target snapshot parts
        paths = target_snapshot.metadata["subvolumes"]
        new_volumes = []

        rootfs = ""
        self.callback.notice("Recovering target snapshot...")
        for item in paths:
            if not full and item["source"] not in parts:
                continue
            source = self.volume.get_subvolume(item["backup"])
            target = item["source"]
            self.callback.notice("Restoring " + source.path + " => " + target)
            new_volumes += source.snapshot_recursive(target)

            target_vol = self.volume.get_subvolume(target)
            if os.path.isfile(target_vol.get_absolute_path() + "/etc/fstab"):
                self.callback.warn("Detected restored rootfs (" + target + "). Fstab will be patched in them!")
                rootfs = target_vol.get_absolute_path()

        # Patch fstab in restored system
        patch_fstab_of_backup(rootfs, new_volumes, self.callback, config)
        self.callback.notice("Restore completed. Reboot is required to apply changes.")

    def _create_snapshot_item(self):
        """
        Create snapshot folder and object
        :return: snapshot object
        """
        if not os.path.isdir(self.storage_path):
            os.mkdir(self.storage_path)

        name = datetime.today().strftime(SNAPSHOT_NAME_FORMAT)
        path = self.storage_path + "/" + name

        self.callback.notice("Backup to: " + path)
        os.mkdir(path)

        snapshot = Snapshot(name, self.volume)
        return snapshot

    def create_snapshot(self, tag_user, info=None):
        """
        Create system snapshot
        :return:
        """
        snapshot = self._create_snapshot_item()

        # Snapshot all partitions
        config = AppConfig()
        recover_paths = []
        for a in config.subvolumes:
            subvolume = self.volume.get_subvolume(a)
            destination = snapshot.path + "/" + subvolume.path
            self.callback.notice("Snapshot recursive: " + subvolume.get_absolute_path() + " => " + destination)
            new_root = subvolume.snapshot_recursive(destination)[0]
            recover_paths.append({
                "backup": new_root.path,
                "source": new_root.original_path
            })

        snapshot.metadata["subvolumes"] = recover_paths
        if tag_user:
            snapshot.set_tag("user")

        # Create snapshot info file (via snapshot class)
        if info != "" and info is not None:
            self.callback.notice("Set snapshot info: " + info)
            snapshot.metadata["info"] = info

        snapshot.save_metadata()
        self.callback.notice("Snapshot created.")

        return snapshot
