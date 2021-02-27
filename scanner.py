from sortedcontainers import SortedList
from os import walk, stat, path, scandir, DirEntry
from time import time
from ticker import should_report, last_report_tm
from configure import Configure

# data struct for storing a file found in the source directory
class FoundFile:
	def __init__(self, dname, fname, fsize, fmtime):
		self.dirname = dname
		self.filename = fname
		self.filesize = fsize
		self.filemodtime = fmtime
		self.order = fmtime   # default ordering is by file modification time

	def fullname(self):
		return path.join(self.dirname, self.filename)

	def age(self):
		sec = time() - self.filemodtime
		minu = int(sec / 60)
		hours = int(minu / 60)
		days = int(hours / 24)
		mont = int(days / 30)
		years = int(mont / 12)
		if minu < 1:
			return '{} sec'.format(sec)
		if hours < 1:
			return '{} min'.format(minu)
		if days < 1:
			return '{} hours'.format(hours)
		if mont < 1:
			return '{} days'.format(days)
		if years < 1:
			return '{} months'.format(mont)
		else:
			return '{} years+{} months'.format(years, mont - years*12)

	def __eq__(self, other):
		return self.order == other.order

	def __lt__(self, other):
		return self.order < other.order



class Scanner:
	def __init__(self):
		# define a sorted list of found files
		self.foundfiles = SortedList()
		# define the total number of found files
		self.num_foundfiles = 0
		self.skipdirs = set([])

	def skipping(self, fullname):
		for sd in self.skipdirs:
			if path.commonpath([fullname, sd]) == sd:
				# should be skipped
				print("fullname={}, sd={}".format(fullname, sd))
				return True
		return False


	def scan_dirtree(self, startpath):
		if self.skipping(startpath):
			return

		if should_report():
			print("SCANNER: have", self.num_foundfiles, ", and now in '", startpath, "'")

		# recursively walk the entire directory tree starting at @startpath
		with scandir(startpath) as it:
			#for (dirpath, dirnames, filenames) in walk(startpath):
			#print("dirpath=", dirpath, ", dirnames=", dirnames, ", filenames=", filenames)
			# go through the files and directories in the scanned dir.
			#for f in filenames:
			for fd in it:
				if fd.is_file():
					# construct full file name
					#fullname = path.join(dirpath, f)
					fullname = fd.path
					# check if it is in the skip-dir prefix
					if self.skipping(fullname):
						continue
					# read file metadata
					sr = fd.stat(follow_symlinks=False)
					# insert metadata into the FoundFile struct and list
					ff = FoundFile(startpath, fd.name, sr.st_size, sr.st_mtime)
					self.foundfiles.add(ff)
					self.num_foundfiles += 1
				
				if fd.is_dir():
					# a directory -> go in.
					self.scan_dirtree(fd.path)

	# scan all files in the configuration directory
	def scan_confdirs(self, cfg):
		self.skipdirs = cfg.skipdirs
		for cd in cfg.scandirs:
			self.scan_dirtree(cd)


