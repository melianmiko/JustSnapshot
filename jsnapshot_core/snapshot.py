import json
import os.path
import shutil
import subprocess
from datetime import datetime


SNAPSHOT_NAME_FORMAT = "%Y-%m-%d_%H-%M-%S"


class Snapshot:
    def __init__(self, name, volume):
        self.name = name
        self.volume = volume
        self.path = self.volume.mount_point + "/_backups" + "/" + name
        self.metadata = {}

        self.load_metadata()

    def get_date(self):
        return datetime.strptime(self.name, SNAPSHOT_NAME_FORMAT)

    def has_tag(self, tag):
        """
        Check that snapshot has 'tag' in metadata.tags
        :param tag: required tag
        :return: True, if has
        """
        if "tags" not in self.metadata:
            return False

        return tag in self.metadata["tags"]

    def set_tag(self, tag):
        """
        Add tag to metadata.tags
        :param tag: required tag
        :return: void
        """
        if "tags" not in self.metadata:
            self.metadata["tags"] = []

        if tag not in self.metadata["tags"]:
            self.metadata["tags"].append(tag)
            self.metadata["tags"].sort()
            self.save_metadata()

    def untag(self, tag):
        """
        Remove tag from snapshot
        :param tag: target tag
        :return: void
        """
        if "tags" not in self.metadata:
            return

        if tag in self.metadata["tags"]:
            self.metadata["tags"].remove(tag)

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
