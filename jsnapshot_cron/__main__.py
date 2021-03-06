#!/usr/bin/env python3
from jsnapshot_core.callback import LogCallback
from jsnapshot_core.initializer import initialize_app
from .cron_engine import handle_cron

# Init app
callback = LogCallback("cron")
result = initialize_app(callback)
if not result:
    callback.error("App init failed")
    raise SystemExit(1)

callback.notice("Processing cron actions...")
handle_cron(callback)

callback.close()
