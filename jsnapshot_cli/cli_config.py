import getpass
import jsnapshot_core

callback = jsnapshot_core.AppCallback()


def main():
    if getpass.getuser() != "root":
        callback.error("Run this command as superuser!")
        raise SystemExit(1)

    app_config = jsnapshot_core.AppConfig()

    # List mounted BTRFS disks, ask user for target
    disks = jsnapshot_core.find_devices()
    colors = jsnapshot_core.ConsoleColor

    print("")
    print(colors.HEADER + colors.BOLD + "STEP 1. Select your system disk." + colors.END)
    print("")
    print("Mounted BTRFS volumes:")

    values = []
    for i, line in enumerate(disks):
        print(" " + str(i) + " - " + line)
        values.append(str(i))

    print("")
    i = callback.question("Enter number of target device to use it.", values)
    target = disks[int(i)]
    app_config.target_device = target
    app_config.save()

    # Init app
    jsnapshot_core.initialize_app(callback)

    # Bind volume, get list of root subvolumes
    volume = jsnapshot_core.bind_root()
    data = volume.list_root_subvolumes()

    print("")
    print(colors.HEADER + colors.BOLD + "STEP 2. Select subvolumes to backup." + colors.END)
    print("")
    print("Available BTRFS sub-volumes:")

    values = []
    for i, item in enumerate(data):
        print(" " + str(i) + " - " + item.path)
        values.append(str(i))

    print("")
    line = callback.input("Enter numbers of volumes separated with space. Example, if you want to backup " +
                          "first and third, enter '0 2'.")

    subvolumes = []
    for a in line.split(" "):
        val = data[int(a)]
        print("Selected subvolume", val)
        subvolumes.append(val.path)

    app_config.subvolumes = subvolumes
    app_config.save()

    print("Configuration updated. Now you can use this application.")
