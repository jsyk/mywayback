import sys, getopt
from os import path
import time
from configure import Configure
from scanner import FoundFile, Scanner
from checker import Checker
from taker import Taker

print("** Welcome to MyWayback! **")


args = sys.argv[1:]

if len(args) == 0:
	print("ERROR: Missing command-line argument!")
	exit(0)

targetbasedir = args[0]
print("Target directory: {}".format(targetbasedir))
snapshotname = time.strftime("%Y-%m-%d--%H-%M")
print("Snaphost name: {}".format(snapshotname))

cfg = Configure()
cfg.read_configdir(path.join(targetbasedir, 'config'))
print("Scan dirs (+):")
print(cfg.scandirs)
print("Skip dirs (-):")
print(cfg.skipdirs)


sca = Scanner()
#s.scan_dirtree('/home/jara/Dokumenty')
sca.scan_confdirs(cfg)
print()
print("SCANNER FINISHED: Number of found files: {}".format(sca.num_foundfiles))
print()

# for i in range(0, 10):
# 	ff = s.foundfiles.pop()
# 	print(ff.order, ff.fullname())

che = Checker(targetbasedir)
tak = Taker(targetbasedir, snapshotname)
batchsize = 1000

while sca.foundfiles or che.digestedfiles:
	che.digest_files(sca, batchsize)
	tak.take_files(che, batchsize)

print("** Finished a backup run with MyWayback! **")
