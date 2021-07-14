import shutil
import subprocess
import re
import os


def parse_show_line(line):
    """
    Read 'btrfs show' line and return key and value
    :param line: Source line
    :return: Key and value
    """
    line = line.replace("\t", " ")
    line = re.sub(" +", " ", line)

    parts = line.split(":")
    key = parts[0].strip()
    value = parts[1].strip()

    return key, value


class BtrfsSubvolume:
    """
    BTRFS Subvolume path
    """
    def __init__(self, volume_id, volume):
        """
        Default constructor
        :param volume_id: Subvolume ID
        :param volume: BTRFS Volume class object
        """
        self.volume = volume
        self.id = 0
        self.path = ""
        self.original_path = ""
        self.size_full = ""
        self.size_unique = ""

        if isinstance(volume_id, int):
            self.id = volume_id
            self._load_data_from_id()
        elif isinstance(volume_id, str):
            self.path = volume_id
            self._load_data_from_path()

        # Check that all is loaded
        assert self.path != ""
        assert self.id != 0

    def get_absolute_path(self):
        """
        Get absolute path of subvolume, eg. disk mount point + subvolume path
        :return:
        """
        if self.path.startswith(self.volume.mount_point):
            # Is absolute
            return self.path

        return self.volume.mount_point + "/" + self.path

    def find_child_volumes(self):
        """
        Get list of child subvolumes
        :return:
        """
        return self.volume.get_subvolumes_inside(self.path)

    def _load_data_from_id(self):
        """
        Load all data from subvolume ID
        :return: void
        """
        command = ["btrfs", "subvolume", "show", "--rootid", str(self.id), self.volume.mount_point]
        self._load_data(command)

    def _load_data_from_path(self):
        """
        Load all data from relative subvolume path
        :return: void
        """
        command = ["btrfs", "subvolume", "show", self.get_absolute_path()]
        self._load_data(command)

    def _load_data(self, command):
        """
        Load all subvolume data
        :return: void
        """
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        rows = str(result.stdout, "utf8").split("\n")
        self.path = rows[0]

        # Parse properties
        for line in rows[1:]:
            if ":" in line:
                key, value = parse_show_line(line)
                if key == 'Usage referenced':
                    self.size_full = value
                elif key == "Usage exclusive":
                    self.size_unique = value
                elif key == "Subvolume ID":
                    self.id = int(value)

    def __str__(self):
        """
        Convert this object to string
        :return: String with subvolume ID and full system path
        """
        return str(self.id) + " " + self.volume.mount_point + "/" + self.path

    def snapshot_recursive(self, destination):
        if not destination.startswith(self.volume.mount_point):
            destination = self.volume.mount_point + "/" + destination

        # Snapshot self directly to destination
        root_snapshot = self.snapshot(destination)

        # Snapshot child volumes
        child_volumes = self.find_child_volumes()
        created_snaps = [root_snapshot]
        for volume in child_volumes:
            rel_path = volume.path[len(self.path) + 1:]
            # Btrfs by default creates empty directories
            # for children subvolumes when creating snapshot
            # and we need to delete them
            os.rmdir(destination + "/" + rel_path)
            new_snap = volume.snapshot(destination + "/" + rel_path)
            created_snaps.append(new_snap)

        return created_snaps

    def exists(self):
        """
        Check that this subvolume exists.
        :return: True, if exists
        """
        return os.path.isdir(self.get_absolute_path())

    def snapshot(self, destination):
        """
        Snapshot this subvolume to 'destination' path
        :param destination: Target path
        :return: void
        """
        if not destination.startswith(self.volume.mount_point):
            destination = self.volume.mount_point + "/" + destination

        assert not os.path.exists(destination)

        command = ["btrfs", "subvolume", "snapshot", self.get_absolute_path(), destination]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        subvolume = BtrfsSubvolume(destination, self.volume)
        subvolume.original_path = self.path
        return subvolume

    def delete_recursive(self):
        """
        VERY VERY DANGER!!! Delete this subvolume and all children's
        :return: True, if success
        """
        sub_volumes = self.find_child_volumes()

        for a in sub_volumes:
            if a.exists():
                a.delete_recursive()

        self.delete()
        return True

    def delete(self):
        """
        DANGER: Delete this subvolume
        :return: True, if success
        """
        command = ['btrfs', "subvolume", "delete", self.get_absolute_path()]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        return True

    def move(self, destination):
        """
        DANGER: Move this subvolume to another path
        :param destination: New path
        :return: self, if success
        """
        if not destination.startswith(self.volume.mount_point):
            destination = self.volume.mount_point + "/" + destination

        assert not os.path.exists(destination)

        shutil.move(self.get_absolute_path(), destination)

        self.original_path = self.path
        self.path = destination
        self._load_data_from_path()

        return self
