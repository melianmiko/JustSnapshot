import os.path
from datetime import datetime, timedelta

import jsnapshot_core
from jsnapshot_core.config import AppConfig
from jsnapshot_core.engine import BackupEngine

CRON_FILE = "/etc/cron.hourly/00-just-snapshot"
PERIOD_NAMES = ["hourly", "daily", "weekly", "monthly"]
PERIOD_LENGTH = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(days=7),
    "monthly": timedelta(days=30)
}


def process_tag_cleanup(engine, config, callback):
    """
    This function will remove period tag from snapshot if
    count of tagged snapshots is bigger than count in config.

    :param engine: Target backup engine
    :param config: App config
    :param callback: Callback
    :return: void
    """
    for period in PERIOD_NAMES:
        tagged = engine.list_snapshots_with_tag(period)
        while len(tagged) > config.timetable[period]:
            callback.notice("Removing tag " + period + " from " + tagged[0].name)
            tagged[0].untag(period)
            tagged.remove(tagged[0])


def remove_without_tags(engine, callback):
    snaps = engine.list_snapshots()
    for a in snaps:
        if len(a.metadata["tags"]) == 0:
            callback.notice("DELETE non-required snapshot: " + a.name)
            a.delete()


def handle_cron(callback):
    volume = jsnapshot_core.bind_root()
    engine = BackupEngine(callback, volume)
    now = datetime.today()
    config = AppConfig()

    for period in PERIOD_NAMES:
        if config.timetable[period] == 0:
            callback.notice("Skip period " + period)
            continue

        callback.notice("Processing " + period)
        limit = now - PERIOD_LENGTH[period]

        tagged = engine.list_snapshots_with_tag(period)
        if len(tagged) > 0:
            # Check that last tagged snapshot is actual
            # Skip period, if true
            last_tagged = tagged[-1]
            if last_tagged.get_date() > limit:
                callback.notice("Already created, skipping...")
                continue

        snapshots = engine.list_snapshots()
        if len(snapshots) > 0:
            # Check that last user snapshot is actual
            # Tag them and skip period, if true
            last_snapshot = snapshots[-1]
            if last_snapshot.get_date() > limit:
                callback.notice("Use exiting snapshot for this period: " + last_snapshot.name)
                last_snapshot.set_tag(period)
                continue

        callback.notice("Creating snapshot...")

        snapshot = engine.create_snapshot(False, "Auto backup")
        snapshot.set_tag(period)

    process_tag_cleanup(engine, config, callback)
    remove_without_tags(engine, callback)


def cron_auto_config():
    config = AppConfig()
    is_enabled = False
    for period in PERIOD_NAMES:
        if config.timetable[period] > 0:
            is_enabled = True

    # Setup crontab
    if not is_enabled and os.path.isfile(CRON_FILE):
        os.unlink(CRON_FILE)
    elif is_enabled:
        with open(CRON_FILE, "w") as f:
            f.write("#!/usr/bin/bash\npython3 -m jsnapshot_cron\n")
        os.chmod(CRON_FILE, 0o755)
