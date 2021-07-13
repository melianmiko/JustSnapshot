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
