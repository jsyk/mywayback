from os import walk, stat, path
from ticker import should_report


# the Configure class reads and parses the configuration files
class Configure:
    def __init__(self):
        self.scandirs = []
        self.skipdirs = []

    # walk configuration directory @cfgdir and try to read config from each file in the directory,
    # files are read in the alphabetical order.
    def read_configdir(self, cfgdir):
        for (dirpath, dirnames, filenames) in walk(cfgdir):
            filenames.sort()
            print("dirpath=", dirpath, ", dirnames=", dirnames, ", filenames=", filenames)
            for fn in filenames:
                self.read_config(dirpath, fn)

    # read configuration from a given file
    def read_config(self, dirpath, fname):
        # open and read config file
        fd = open(path.join(dirpath, fname), 'rt')
        cfgall = fd.readlines()
        fd.close()
        #print(cfgall)
        linenum = 0
        for ln in cfgall:
            lns = ln.strip('\n')
            linenum += 1
            if len(lns) == 0:
                continue
            if lns[0] == '+':
                # add the path to scandir
                self.scandirs.append(lns[1:])
            else:
                if lns[0] == '-':
                    self.skipdirs.append(lns[1:])
                else:
                    if lns[0] == '#':
                        # a comment line
                        pass
                    else:
                        print("WARNING: File:Line {}:{} has a wrong format: missing a leading character: +-#".format(fname, linenum) )

