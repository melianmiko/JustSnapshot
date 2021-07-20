import os
import subprocess
from .btrfs_subvolume import BtrfsSubvolume


class BtrfsVolume:
    """
    BTRFS Volume class
    """
    def __init__(self, mount_point):
        """
        Default constructor
        :param mount_point: Volume mount point
        """
        self.mount_point = mount_point

        assert os.path.exists(mount_point)

    def list_subvolumes(self):
        """
        Get list of subvolumes
        :return: List of BtrfsSubvolume objects
        """
        subvolumes = []
        command = ["btrfs", "subvolume", "list", self.mount_point]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        data_lines = str(result.stdout, "utf8").split("\n")
        for line in data_lines:
            if not line == "":
                line = line.split(" ")
                volume_id = int(line[1])
                assert volume_id > 0

                subvolumes.append(BtrfsSubvolume(volume_id, self))

        return subvolumes

    def get_subvolumes_inside(self, path):
        """
        Get list of subvolumes inside path
        :param path: Target search path
        :return:
        """
        if path.startswith(self.mount_point):
            path = path[len(self.mount_point)+1:]

        out = []
        command = ["btrfs", "subvolume", "list", self.mount_point]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        data_lines = str(result.stdout, "utf8").split("\n")
        for line in data_lines:
            if not line == "":
                line = line.split(" ")
                volume_id = int(line[1])
                volume_path = line[8]
                assert volume_id > 0

                if volume_path.startswith(path + "/") and volume_path != path:
                    out.append(BtrfsSubvolume(volume_id, self))

        return out

    def get_subvolume(self, path):
        """
        Get subvolume by name or relative path
        :param path: Target path
        :return: BtrfsSubvolume or False, if not found
        """
        return BtrfsSubvolume(path, self)

    def create_subvolume(self, path):
        if not path.startswith(self.mount_point):
            path = self.mount_point + "/" + path

        assert not os.path.exists(path)
        command = ["btrfs", "subvolume", "create", path]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        return BtrfsSubvolume(path, self)

    def list_root_subvolumes(self):
        """
        Get list of root subvolumes
        :return: list
        """
        out = []
        command = ["btrfs", "subvolume", "list", self.mount_point]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        assert result.returncode == 0

        data_lines = str(result.stdout, "utf8").split("\n")
        for line in data_lines:
            if not line == "":
                line = line.split(" ")
                volume_id = int(line[1])
                volume_path = line[8]
                assert volume_id > 0

                if "/" not in volume_path:
                    out.append(BtrfsSubvolume(volume_id, self))

        return out
