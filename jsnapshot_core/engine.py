import json
import os.path

from datetime import datetime

import jsnapshot_core


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
            out.append(jsnapshot_core.Snapshot(name, self.volume))

        return out

    def create_snapshot(self, info=None):
        """
        Create system snapshot
        :return:
        """
        if not os.path.isdir(self.storage_path):
            os.mkdir(self.storage_path)

        name = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
        path = self.storage_path + "/" + name

        self.callback.notice("Backup to: " + path)
        os.mkdir(path)

        # Snapshot all partitions
        config = jsnapshot_core.AppConfig()
        targets = []
        for a in config.subvolumes:
            subvolume = self.volume.get_subvolume(a)
            destination = path + "/" + subvolume.path
            self.callback.notice("Snapshot recursive: " + subvolume.get_absolute_path() + " => " + destination)
            targets.append(subvolume.snapshot_recursive(destination)[0])

        # Create recover map file
        recover_paths = []
        for item in targets:
            recover_paths.append({
                "backup": item.path,
                "source": item.original_path
            })

        with open(path + "/recover_paths.json", "w") as f:
            json.dump(recover_paths, f)

        # Create snapshot info file (via snapshot class)
        snapshot = jsnapshot_core.Snapshot(name, self.volume)
        if info != "" and info is not None:
            self.callback.notice("Set snapshot info: " + info)
            snapshot.metadata["info"] = info
        snapshot.save_metadata()

        self.callback.notice("Snapshot created.")
