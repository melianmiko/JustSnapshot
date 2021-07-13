import argparse
import json
import os.path
import sys
import traceback

import jsnapshot_core


def create():
    """
    Create snapshot CLI handler
    :return: void
    """
    parser = argparse.ArgumentParser(prog="jsnapshot create", description="Create new system snapshot")
    parser.add_argument("--info", default="", required=False, type=str, help="User comment for snapshot")
    args, leftovers = parser.parse_known_args(args=sys.argv[2:])

    callback = jsnapshot_core.AppCallback()
    result = jsnapshot_core.initialize_app(callback)
    if not result:
        callback.error("App init failed")
        raise SystemExit(1)

    volume = jsnapshot_core.bind_root()
    engine = jsnapshot_core.BackupEngine(callback, volume)
    try:
        engine.create_snapshot(info=args.info)
    except Exception:
        traceback.print_exc()
        callback.error("Operation failed.")
        raise SystemExit(1)


def restore():
    """
    Restore snapshot CLI handler
    :return: void
    """
    pass


def show():
    """
    Show backup CLI handler
    :return: void
    """
    parser = argparse.ArgumentParser(prog="jsnapshot show", description="Get snapshot info.")
    parser.add_argument("snapshot", type=str, help="Snapshot name")
    args = parser.parse_args(args=sys.argv[2:])
    name = args.snapshot

    callback = jsnapshot_core.AppCallback()
    result = jsnapshot_core.initialize_app(callback)
    if not result:
        callback.error("App init failed")
        raise SystemExit(1)

    volume = jsnapshot_core.bind_root()
    engine = jsnapshot_core.BackupEngine(callback, volume)
    snapshots = engine.list_snapshots()

    item = None
    for a in snapshots:
        if a.name == name:
            item = a

    if item is None:
        callback.warn("Snapshot with name " + name + " not found")
        raise SystemExit(1)

    KEY_WIDTH = 32
    colors = jsnapshot_core.ConsoleColor

    print()
    print(colors.BOLD + "Snapshot metadata:" + colors.END)
    for a in item.metadata:
        print(" " + a.ljust(KEY_WIDTH) + " = " + item.metadata[a])
    print()

    # Read recover_paths file
    if not os.path.isfile(item.path + "/recover_paths.json"):
        callback.error("Snapshot is broken: missing recovery paths file")
        raise SystemExit(2)

    with open(item.path + "/recover_paths.json", "r") as f:
        parts = json.load(f)

    for info in parts:
        print(colors.BOLD + "Subvolume " + info["backup"] + ":" + colors.END)
        print(" " + "Source path".ljust(KEY_WIDTH) + " = " + info["source"])

        subvolume = volume.get_subvolume(info["backup"])
        if not subvolume.exists():
            callback.error("Snapshot is broken: one or more subvolume not found")
            raise SystemExit(2)

        print(" " + "Full size".ljust(KEY_WIDTH) + " = " + subvolume.size_full)
        print(" " + "Unique size".ljust(KEY_WIDTH) + " = " + subvolume.size_unique)

        print()


def list_backups():
    """
    List snapshots CLI handler
    :return: void
    """
    parser = argparse.ArgumentParser(prog="jsnapshot list", description="List available snapshots")
    parser.parse_known_args(args=sys.argv[2:])

    callback = jsnapshot_core.AppCallback()
    result = jsnapshot_core.initialize_app(callback)
    if not result:
        callback.error("App init failed")
        raise SystemExit(1)

    volume = jsnapshot_core.bind_root()
    engine = jsnapshot_core.BackupEngine(callback, volume)
    snapshots = engine.list_snapshots()

    for snapshot in snapshots:
        info = ""
        if "info" in snapshot.metadata:
            info = snapshot.metadata["info"]
        print(snapshot.name.ljust(24), info)


def delete():
    """
    Delete snapshot CLI handler
    :return: void
    """
    parser = argparse.ArgumentParser(prog="jsnapshot delete", description="Delete one snapshot.")
    parser.add_argument("snapshot", type=str, help="Snapshot name")
    args = parser.parse_args(args=sys.argv[2:])
    name = args.snapshot

    callback = jsnapshot_core.AppCallback()
    result = jsnapshot_core.initialize_app(callback)
    if not result:
        callback.error("App init failed")
        raise SystemExit(1)

    volume = jsnapshot_core.bind_root()
    engine = jsnapshot_core.BackupEngine(callback, volume)
    snapshots = engine.list_snapshots()

    item = None
    for a in snapshots:
        if a.name == name:
            item = a

    if item is None:
        callback.warn("Snapshot with name " + name + " not found")
        raise SystemExit(1)

    callback.notice("Deleting snapshot " + item.path)
    item.delete()
