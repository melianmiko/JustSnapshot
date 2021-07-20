import time
from datetime import datetime
from pathlib import Path

from .app_info import VERSION


class ConsoleColor:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    GRAY = '\033[90m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LogCallback:
    def __init__(self, tag):
        date_string = datetime.today().strftime("%Y-%m-%d_%H-%M-%S\n")
        header = "\n-------------------------\n"
        header += "JustSnapshot " + tag + " " + VERSION + " at " + date_string

        log_root = "/var/log/just_snapshot"
        if not Path(log_root).is_dir():
            Path(log_root).mkdir()

        self.path = log_root + "/" + tag + ".log"
        if Path(self.path).exists():
            # If file is older than 31 day, rename to backup
            if Path(self.path).stat().st_ctime < time.time() - 31 * 24 * 3600:
                Path(self.path).rename(self.path + "_" + date_string)
        else:
            # Touch file
            Path(self.path).touch()

        self.file = open(self.path, "a")
        self.file.write(header)

    def notice(self, data):
        self.file.write("NOTICE: " + str(data) + "\n")

    def warn(self, data):
        self.file.write("WARN: " + str(data) + "\n")

    def error(self, data):
        self.file.write("ERROR: " + str(data) + "\n")

    def close(self):
        self.file.close()


# noinspection PyMethodMayBeStatic
class AppCallback:
    def notice(self, data):
        print(ConsoleColor.CYAN + ConsoleColor.BOLD + "Notice: " + ConsoleColor.END, data)

    def warn(self, data):
        print(ConsoleColor.WARNING + ConsoleColor.BOLD + "Warning: " + ConsoleColor.END, data)

    def error(self, data):
        print(ConsoleColor.FAIL + ConsoleColor.BOLD + "Error: " + ConsoleColor.END, data)

    def input(self, question):
        print(ConsoleColor.BOLD + question + ConsoleColor.END)
        response = ""
        while response == "":
            response = input("Value: ")

        return response

    def question(self, question, answers):
        print(ConsoleColor.BOLD + question + ConsoleColor.END)

        response = "__none__"
        while response not in answers:
            response = input("Enter your choice " + str(answers) + ": ")

        return response
