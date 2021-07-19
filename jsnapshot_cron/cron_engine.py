import os.path
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from crontab import CronTab

import jsnapshot_core
from jsnapshot_core.config import AppConfig
from jsnapshot_core.engine import BackupEngine

CRON_FILE = "/etc/cron.d/just_snapshot"
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

    # process_tag_cleanup(engine, config, callback)


def cron_auto_config():
    config = AppConfig()
    is_enabled = False
    for period in PERIOD_NAMES:
        if config.timetable[period] > 0:
            is_enabled = True

    # Setup crontab
    if not os.path.isfile(CRON_FILE):
        Path(CRON_FILE).touch()

    cron = CronTab(user="root", tabfile=CRON_FILE)
    cron.remove_all()

    if is_enabled:
        job = cron.new(command="/usr/bin/env python3 -m jsnapshot_cron")
        job.minute.on(0)

    cron.write()
    subprocess.run(["service", "cron", "restart"])
