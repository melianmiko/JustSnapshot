import json
import os.path
import shutil


class Snapshot:
    def __init__(self, name, volume):
        self.name = name
        self.volume = volume
        self.path = self.volume.mount_point + "/_backups" + "/" + name
        self.metadata = {}

        self.load_metadata()

    def load_metadata(self):
        if not os.path.isfile(self.path + "/meta.json"):
            return

        with open(self.path + "/meta.json", "r") as f:
            self.metadata = json.load(f)

    def save_metadata(self):
        with open(self.path + "/meta.json", "w") as f:
            json.dump(self.metadata, f)

    def delete(self):
        # Delete included subvolumes
        vols = self.volume.get_subvolumes_inside(self.path)
        for subvolume in vols:
            if subvolume.exists():
                subvolume.delete_recursive()

        shutil.rmtree(self.path)
