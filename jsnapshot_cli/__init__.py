import sys

from . import cli_config, cli_engine

COMMANDS_HELP = """
 jsnapshot [COMMAND] ...

 Just snapshot it!
 Simple BTRFS system snapshot/recover tool.
 
 Commands:
   config           Configure this application
   create           Create new snapshot
   list             List available snapshots
   show             Show backup info
   restore          (DANGER) Recover snapshot
   delete           (DANGER) Delete snapshot
   
 
 To get more information, run some command with '--help' argument.
"""

COMMAND_HANDLERS = {
    "config": cli_config.main,
    "create": cli_engine.create,
    "restore": cli_engine.restore,
    "list": cli_engine.list_backups,
    "delete": cli_engine.delete,
    "show": cli_engine.show
}


def main():
    if len(sys.argv) < 2:
        print(COMMANDS_HELP)
        raise SystemExit(1)

    command = sys.argv[1]
    if command not in COMMAND_HANDLERS:
        print(COMMANDS_HELP)
        raise SystemExit(1)

    COMMAND_HANDLERS[command]()
