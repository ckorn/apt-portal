#!/usr/bin/python
#
#  (C) Copyright 2009, TUXBRAIN S.L. - http://www.tuxbrain.com
#  --------------------------------------------------------------------
#  Based on apt2sql.py from  GetDeb Team - https://launchpad.net/~getdeb
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  --------------------------------------------------------------------
#
#  This file imports opkg packages from a repository to an sql database
#  control files.

"""
Usage:
    opkg2sql.py [--database mysql://user:password@localhost/apt2sql] \
        [archive_root_url version arquitecture1[,arquetecture2,... ] 
        
Example:
    opkg2sql.py http://build.shr-project.org shr-unstable all
    
"""

# sqlalchemy uses a deprecated module
import warnings
warnings.simplefilter("ignore",DeprecationWarning)

import sys
import os
import socket
import urllib2
import zlib
import gzip
import tempfile
import re
from datetime import datetime
from optparse import OptionParser
from urllib2 import Request, urlopen, URLError, HTTPError
from localaux import *
from packages_model import *
from dpkg_control import *
from lockfile import *
    
Log = Logger()
	
def get_last_mofified_time(file_url):
	"""
	Returns the last mofidifed time for the specified url
	"""
	try:
		f = urllib2.urlopen(file_url)
	except HTTPError, e:        
		Log.print_("Error %s : %s" % (e.code, file_url))
		return None	
	last_modified = f.info()['Last-Modified']		
	f.close()	
	d_last_modified = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
	return d_last_modified	
#Due opkg lacks of Release file and informed PackageList 
#this is a simplified version of the original apt2sql.py fuction 	
#avoinding checkings done using those files
#TODO Maybe some arch checkings can be done scaning directories directly from 
#     the html returned of the archive_url/version/ikpg directory
def import_repository(archive_url, version, architectures, check_file):
	"""
	Import a repository into the dabase
	"""
	# Now let's import the Packages file for each architecture
	# Some redundancies and fixes values where done to mantain the same 
	# class structure of Package and PackageList
	# TODO opkg is also used in OpenWRT based distros so we must find a way
	#      to discrimite the Origin value now is hardcoded to "OE" 
	for arch in architectures:
		packages_file = "%s/%s/ipk/%s/Packages.gz" \
			% (archive_url, version, arch)
		packagelist = \
			PackageList.query.filter_by( \
				version = version, \
				architecture = arch).first() \
			or \
			PackageList( \
				suite = version, \
					version = version, \
					component = version, \
					origin = "OE", \
					label = "", \
					architecture = arch, \
					description = "", \
					date = get_last_mofified_time(packages_file)\
					)            
		check_list=create_check_visibility_list(check_file)
		import_packages_file(archive_url, packagelist, packages_file, version, check_list)
		packagelist = None


def import_packages_file(archive_url, packagelist, packages_file, distro_version, check_list):
	"""
        Imports packages information from a packages file
	"""
		
	Log.log("Downloading %s" % packages_file)
	try:
		f = urllib2.urlopen(packages_file)
	except HTTPError, e:
		session.rollback() # Rollback the suite insert
		print "%s : %s" % (e.code, packages_file)
		return -1
	data = f.read()
	f.close()      
	
    # Decompress the file contents
	tmpfile = tempfile.NamedTemporaryFile(delete = False)
	tmpfile.write(data)
	tmpfile.close()
	f = gzip.open(tmpfile.name)
	data = f.read()
	f.close()
	os.unlink(tmpfile.name)
	keep_packages_list = [] # info from packages loaded from the file
	
	for package_info in data.split("\n\n"):
		if (not package_info or package_info.replace('\n','') == '') : 
		# happens at the end of the file
			continue
		control = DebianControlFile(contents = package_info)
		package_name = control['Package']
		source = control['Source']
		version = control['Version']
		architecture = control['Architecture']
		description = 	control['Description']
		homepage = 	control['HomePage']	
		package = Package.query.filter_by( \
			package = package_name, \
			version = version, \
			architecture = architecture).first()
		if not package: # New package			
			opk_filename = "%s/%s/ipk/%s/%s" % (archive_url, distro_version, architecture, control['Filename'])
			last_modified = get_last_mofified_time(opk_filename)
			is_visible = check_visibility(package_name, check_list)
			Log.print_("Inserting %s %s %s %s visible=%s" % (package_name, source \
				, version, architecture, is_visible))
			package = Package( 
				package = package_name \
				, source = source \
				, version = version \
				, architecture = architecture \
				, last_modified = last_modified \
				, description = description \
				, homepage = homepage \
				, is_visible = is_visible \
			)
		# Create relation if needed
		if not packagelist in package.lists:
			Log.print_("Including %s -> %s" % (package, packagelist))
			package.lists.append(packagelist)
		# Add to in memory list to skip removal
		keep_packages_list.append("%s %s %s" % 
			(package.package, package.version, package.architecture))            
	# Remove all relations to packages which were not imported
	# on the loop above
	must_remove = []
	for package in packagelist.packages:
		list_item = "%s %s %s" % (package.package, package.version \
			, package.architecture)			
		if list_item in keep_packages_list:
			keep_packages_list.remove(list_item)
		else:
			Log.print_("Removing %s" % `package`)
			must_remove.append(package)        
	for package in must_remove:
		packagelist.packages.remove(package)
	session.commit()
	del data
	
def create_check_visibility_list(check_file):
	check_list = list()
	if check_file:
		for line in open(check_file):
			if not line.strip():
	        		continue                         
			if line.startswith("#"):
	        		continue
			check_list.append(re.compile(line.strip()))
	return check_list
		
def check_visibility(package,check_list):
	visibility = True
	for check in check_list:
		match = check.search(package)
		if match:
			visibility = False
			break
	return visibility			 	

def main():
	
	parser = OptionParser()
	parser.add_option("-d", "--database",
		action = "store", type="string", dest="database",
		help = "specificy the database URI\n\n" \
		"Examples\n\n" \
		"   mysql://user:password@localhost/apt2sql" \
		"   sqlite:///apt2sql.db" \
	)
	parser.add_option("-c", "--check_visibility",
		action = "store", type="string", dest="check_file",
	        help = "specificy text file containig regexp to exclude packages\n\n" \
	)                                                                                                   
	parser.add_option("-f", "--force-rpool",
		action = "store_true", dest="rpool", default=False,
		help = "force to use rpool path instead of pool")				
	parser.add_option("-q", "--quiet",
		action = "store_false", dest="verbose", default=True,
		help = "don't print status messages to stdout")
	parser.add_option("-r", "--recreate-tables",
		action = "store_true", dest="recreate_tables", default=False,
		help = "recreate db tables")            		
	parser.add_option("-s", "--sql-echo",
		action = "store_true", dest="sql_echo", default=False,
		help = "echo the sql statements")
	(options, args) = parser.parse_args()
	db_url = options.database or "sqlite:///apt2sql.db"
	check_file = options.check_file
	Log.print_(check_file)
	if len(args) < 2:
		print "Usage: %s " \
			"archive_root_url suite [component1[, component2] ]" \
			% os.path.basename(__file__)
		sys.exit(2)

	archive_url = args[0]
	version = args[1]
	architectures = None
	if len(args) > 2:
		architectures = args[2].split(",")    
	    

	Log.verbose = options.verbose	    
	
	try:
		lock = LockFile("opkg2sql")
	except LockFile.AlreadyLockedError:
		Log.log("Unable to acquire lock, exiting")
		return

	# We set the database engine here
	metadata.bind = db_url        
	metadata.bind.echo = options.sql_echo    
	setup_all(True)
	if options.recreate_tables:
		drop_all()
		setup_all(True)

	import_repository(archive_url, version, architectures,check_file)
	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'User requested interrupt'
		sys.exit(1)
