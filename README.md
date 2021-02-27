# mywayback
A deduplicating automatic backup tool


Install Dependencies
--------------------
1) python3 @ windows, linux
2) pip install sortedcontainers --user


Running
-------
python mywayback.py <target-directory>


Target Directory Content
------------------------
The <target-directory> specified on the command line MUST contain a subdirectory named 'config/'.
Files in the 'config/' subdirectory are read in alphabetical order as the configuration files. File extensions are irrelevant.
Content of a configuration file must be:

	# comment
	+/some/directory/to/backup
	-/some/other/directory/to/skip

The tool creates in the target directory two new subdirs:

	db/			This contains the name-hash database in the db/by-name, and the main data in the db/by-hash. DO NOT TOUCH ANYTHING UNDER.
	snapshot/	Here with each run a new backup snapshot with the data and time is created and filled. Files here are hard-links to 
				the main data in the db/by-hash directory.

