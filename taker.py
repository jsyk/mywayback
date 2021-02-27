from sortedcontainers import SortedList
from ticker import should_report
from scanner import FoundFile, Scanner
from checker import Checker, split_hexdigest_to_dirpath, path_sanitize
import hashlib
import os
from os import path
from shutil import copy2


class Taker:
    def __init__(self, archroot, viewname):
        self.root = archroot
        self.viewroot = path.join(archroot, 'snapshot', viewname)
        self.total_newbytes = 0
        self.num_takenfiles = 0

    def take_files(self, checker, batchsize):
        batchcnt = 0
        while checker.digestedfiles and (batchcnt < batchsize):
            ff = checker.digestedfiles.pop()
            batchcnt += 1
            if should_report():
                print("TAKER: {}, taken {} / todo {}, copied {}GB".format(ff.age(), self.num_takenfiles, 
                    len(checker.digestedfiles), round(self.total_newbytes/1024/1024/1024, 1)))

            # conver file digest to path
            hdir = split_hexdigest_to_dirpath(ff.digest)
            fullhdir = path.join(self.root, 'db', 'by-hash', hdir)
            bodyfile = path.join(fullhdir, 'body')
            if not path.isdir(fullhdir):
                # a new file
                os.makedirs(fullhdir)
                try:
                    # shutil.copy2() should copy metadata: permission bits, last access time, last modification time, and flags
                    copy2(ff.fullname(), bodyfile, follow_symlinks=False)
                except FileNotFoundError:
                    # file removed inbetween?
                    print("TAKER WARN: File not found, maybe removed: ", ff.fullname())
                    continue

                self.total_newbytes += ff.filesize

            # link in to the view
            dirname_decorated = path_sanitize(ff.dirname)
            viewdir = path.join(self.viewroot, dirname_decorated)
            viewfname = path.join(viewdir, ff.filename)
            # print('bodyfile=', bodyfile)
            # print('Viewdir=', viewdir, ', viewfname=', viewfname)
            os.makedirs(viewdir, exist_ok=True)
            try:
                os.link(bodyfile, viewfname)

                self.num_takenfiles += 1

                # note in the hash object the new view name    
                nmlist = open(path.join(fullhdir, 'names'), 'at', encoding="utf8")
                nmlist.write(viewfname)
                nmlist.write('\0\n')
                nmlist.close()

            except FileExistsError:
                # re-running archival to the same dir..? ignore the exception
                pass

