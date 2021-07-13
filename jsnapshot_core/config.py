import json
import os.path

APP_SESSION_HOME = "/run/jsnapshot"
APP_DISK_MOUNT_POINT = APP_SESSION_HOME + "/disk"
APP_CONFIG_FILE = "/etc/just_snapshot.json"


class AppConfig:
    def __init__(self):
        self.target_device = ""
        self.subvolumes = []
        self.timetable = {}

        self.load_config()

    def load_config(self):
        if not os.path.isfile(APP_CONFIG_FILE):
            return

        with open(APP_CONFIG_FILE, "r") as f:
            data = json.loads(f.read())
            self.target_device = data["target_device"]
            self.subvolumes = data["subvolumes"]
            self.timetable = data["timetable"]

    def save(self):
        data = json.dumps({
            "target_device": self.target_device,
            "subvolumes": self.subvolumes,
            "timetable": self.timetable
        })

        with open(APP_CONFIG_FILE, "w") as f:
            f.write(data)

        return True

    def is_valid(self):
        if self.target_device == "":
            return False

        return True
