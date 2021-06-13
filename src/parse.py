# For parsing user config file

def parse(fn):

    f = open(fn, "r")

    files = []
    config = []

    gather_files = False
    gather_config = False

    for line in f.readlines():
        print(line)

        if gather_files and not gather_config:
            try:
                files.append([line.split(",")[0], float(line.split(",")[1])])
            except:
                continue
        elif gather_config and not gather_files:
            config.append("configline")

        if "# Input Files" in line:
            gather_files = True
        elif "# Configuration" in line:
            gather_files = False
            gather_config = True
        else:
            continue

    print(files)
    print(config)

parse("./test.cfg")