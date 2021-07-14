import re


class FstabRow:
    def __init__(self, text):
        self.device = ""
        self.target = ""
        self.type = ""
        self.flags = {}
        self.check_1 = 0
        self.check_2 = 0
        self.valid = False

        self.parse_line(text)

    def read_flags(self, line):
        options = line.split(",")

        for column in options:
            if "=" in column:
                # Split to key and value
                key = column[0:column.index("=")]
                value = column[column.index("=")+1:]
                self.flags[key] = value
            else:
                # Value = true
                self.flags[column] = True

    # noinspection PyBroadException
    def parse_line(self, line):
        line = line.replace("\t", " ")
        line = re.sub(" +", " ", line)
        if line == "":
            return

        data = line.split(" ")
        try:
            self.device = data[0]
            self.target = data[1]
            self.type = data[2]
            self.read_flags(data[3])
            self.check_1 = int(data[4])
            self.check_2 = int(data[5])
            self.valid = True
        except Exception:
            self.valid = False

    def _str_flags(self):
        out = ""

        for key in self.flags:
            out += key
            if not isinstance(self.flags[key], bool):
                out += "=" + str(self.flags[key])
            out += ","

        return out[:-1]

    def __str__(self):
        line = self.device.ljust(24) + " " + \
               self.target.ljust(16) + " " + \
               self.type.ljust(8) + " " + \
               self._str_flags().ljust(32) + " " + \
               str(self.check_1) + " " + \
               str(self.check_2)

        return line


class FstabFile:
    def __init__(self, path=None):
        self.path = path
        self.records = []

        if path is not None:
            self.read()

    def __str__(self):
        out = ""
        for a in self.records:
            out += str(a) + "\n"

        return out

    def save(self):
        out = ""
        for a in self.records:
            out += str(a) + "\n"

        with open(self.path, "w") as f:
            f.write(out)

    def read(self):
        with open(self.path, "r") as f:
            data = f.read().split("\n")

        for line in data:
            row = FstabRow(line)
            if row.valid:
                self.records.append(row)
