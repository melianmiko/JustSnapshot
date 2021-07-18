import getpass
import os.path
import subprocess

from . import config


def initialize_app(callback):
    # Check user
    if getpass.getuser() != "root":
        callback.error("You must run this app as root user.")
        return False

    # Create app session home
    if not os.path.isdir(config.APP_SESSION_HOME):
        os.mkdir(config.APP_SESSION_HOME)
        os.chmod(config.APP_SESSION_HOME, 0o700)

    # Read app config
    app_config = config.AppConfig()
    if not app_config.is_valid():
        callback.error("Application not configured")
        return False

    # Create mount point
    if not os.path.isdir(config.APP_DISK_MOUNT_POINT):
        os.mkdir(config.APP_DISK_MOUNT_POINT)

    # Mount root disk
    mounts = get_mounts()
    if config.APP_DISK_MOUNT_POINT in mounts:
        if mounts[config.APP_DISK_MOUNT_POINT] != app_config.target_device:
            callback.notice("Re-mounting target disk...")
            result = subprocess.run(["umount", config.APP_DISK_MOUNT_POINT])
            assert result.returncode == 0
            result = subprocess.run(["mount", "-o", "subvol=/", app_config.target_device, config.APP_DISK_MOUNT_POINT])
            assert result.returncode == 0
    else:
        result = subprocess.run(["mount", "-o", "subvol=/", app_config.target_device, config.APP_DISK_MOUNT_POINT])
        assert result.returncode == 0

    return True

def get_mounts():
    mounts = {}

    for line in str(subprocess.check_output(['mount', '-l']), "utf8").split('\n'):
        parts = line.split(' ')
        if len(parts) > 2:
            mounts[parts[2]] = parts[0]

    return mounts
