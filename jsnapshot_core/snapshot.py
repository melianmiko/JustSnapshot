import json
import os.path
import shutil
import subprocess


class Snapshot:
    def __init__(self, name, volume):
        self.name = name
        self.volume = volume
        self.path = self.volume.mount_point + "/_backups" + "/" + name
        self.metadata = {}

        self.load_metadata()

    def is_booted(self):
        mounts = str(subprocess.check_output(["mount"]))
        subvolumes = self.metadata["subvolumes"]

        for a in subvolumes:
            sv = self.volume.get_subvolume(a["backup"])
            row = "subvolid=" + str(sv.id)
            if row in mounts:
                return True

        return False

    def load_metadata(self):
        if not os.path.isfile(self.path + "/meta.json"):
            return

        with open(self.path + "/meta.json", "r") as f:
            self.metadata = json.load(f)

    def validate(self):
        if "subvolumes" not in self.metadata:
            return False

        subvolumes = self.metadata["subvolumes"]
        if len(subvolumes) < 1:
            return False

        for a in subvolumes:
            if not os.path.isdir(self.volume.mount_point + "/" + a["backup"]):
                return False

        return True

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
