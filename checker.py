from sortedcontainers import SortedList
from ticker import should_report
from scanner import FoundFile, Scanner
from os import path
import os
import hashlib


def sha256sum_of_file(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def split_hexdigest_to_dirpath(digest):
    return path.join(digest[:2], digest[2:6], digest[6:])

def path_sanitize(pathname):
    path1 = path.normpath(pathname).replace(':', '_') # replace ':' by underscocre
    # remove leading slashes
    while (path1[0] == '/') or (path1[0] == '\\'):
        path1 = path1[1:]
    return path1


class Checker:
    def __init__(self, archroot):
        self.root = archroot
        # define a sorted list of found files
        self.digestedfiles = SortedList()
        self.num_digestedfiles = 0


    def digest_files(self, scanner, batchsize):
        batchcnt = 0
        while scanner.foundfiles and (batchcnt < batchsize):
            ff = scanner.foundfiles.pop()
            batchcnt += 1
            # try to find the hash-caching file for ff
            hcachefilename = path.join(self.root, 'db', 'by-name', path_sanitize(ff.fullname()) + '.tbcache')
            try:
                # open the cache file
                hcachefd = open(hcachefilename, 'rt+', encoding="utf8")
                # read variables
                hc_fname = hcachefd.readline().rstrip('\n')
                hc_size = int(hcachefd.readline().rstrip('\n'))
                hc_mtime = float(hcachefd.readline().rstrip('\n'))
                hc_digest = hcachefd.readline().rstrip('\n')
                # compare with ff - check if the cache is valid
                if (hc_fname != ff.fullname()) or (hc_size != ff.filesize) or (hc_mtime != ff.filemodtime):
                    # something is wrong -> the cached digest cannot be used, and the cache should be updated
                    update_cache = True
                else:
                    # correct, use the digest from the cache
                    ff.digest = hc_digest
                    update_cache = False
            except FileNotFoundError:
                # cache file does not exist, so we create a new one
                os.makedirs(path.dirname(hcachefilename), exist_ok=True)
                hcachefd = open(hcachefilename, 'wt+', encoding="utf8")
                update_cache = True
            except ValueError:
                # error in cache file -> rewrite
                hcachefd = open(hcachefilename, 'wt', encoding="utf8")
                update_cache = True

            try:
                if update_cache:
                    # compute the file digest the hard way from the content
                    ff.digest = sha256sum_of_file(ff.fullname())
                    # clear the cache file
                    hcachefd.seek(0)
                    hcachefd.truncate()
                    # write new cache content
                    #print(ff.fullname())
                    hcachefd.write(ff.fullname() + '\n')
                    hcachefd.write('{}\n'.format(ff.filesize))
                    hcachefd.write('{}\n'.format(ff.filemodtime))
                    hcachefd.write('{}\n'.format(ff.digest))

                hcachefd.close()

                if should_report():
                    print("CHECKER: {}, digested {} / todo {}".format(ff.age(), self.num_digestedfiles, len(scanner.foundfiles)))

                self.digestedfiles.add(ff)
                self.num_digestedfiles += 1
            
            except FileNotFoundError:
                # file removed inbetween?
                print("CHECKER WARN: File not found, maybe removed: ", ff.fullname())

