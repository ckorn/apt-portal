#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  (C) Copyright 2009, GetDeb Team - https://launchpad.net/~getdeb
#  --------------------------------------------------------------------
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
#  This file provides several functions to handle debian packages
#  control files.

import os
import commands	 # We need it for the GPG signature verification
import shutil

class DebianControlFile:
	"""
	This class holds all the information from a debian control file.
	It also provides some methods to operate with that information.
	"""
	class FileInfo:
		def __init__(self, md5sum, size, name):			
			self.size = size
			self.md5sum = md5sum
			self.name = name
			
	class FileNotFoundError(Exception):
		""" 
		A file operation was requested an a listed file was not found
		"""
		def __init__(self, filename):
			self.filename = filename
		def __str__(self):
			return repr(self.filename)

	class MD5Error(Exception):
		"""
		The MD5 checksum verification failed during a file copy/move
		operation.
		"""
		def __init__(self, expected_md5, found_md5, name):
			self.expected_md5 = expected_md5
			self.found_md5 = found_md5
			self.name = name
		def __str__(self):
			return repr(self.value1, self.value2, self.value3)


	def __init__(self, filename=None, contents=None):
		self._filename = filename		
		self.load_contents(filename, contents)
			
	def load_contents(self, filename=None, contents=None):
		"""
		Opens the control file and load it's contents into the data
		attribute.
		"""
		self._data = []
		self._deb_info = {}
		last_data = []
		if filename is not None:
			self._filename = filename
			control_file = open(self._filename, 'r')
			self._data = control_file.readlines()
			control_file.close()
		if contents is not None:
			self._data = contents.split("\n")
		last_data = []
		deb_info = {}
		field = None
		for line in self._data:
			try:
				line = unicode(line, 'utf-8')
			except UnicodeDecodeError:
				print "WARNING: Package info contains non utf-8 data, replacing"
				line = unicode(line, 'utf-8', errors='replace')
			line = line.strip("\r\n")
			if not line:
				continue
			if line == '-----BEGIN PGP SIGNATURE-----':
				break
			if line[0] == " ":
				last_data.append(line)
			else:
				if field and len(last_data) > 1:					
					deb_info[field] = last_data
				last_data = []
				(field, sep, value) = line.partition(": ") 
				if sep == ": ":
					last_data = [value]
					deb_info[field] = value
		if field and len(last_data) > 1:					
			deb_info[field] = last_data					
		self._deb_info = deb_info
		
	def files_list(self):
		if not self['Files']:
			return None
		files = self['Files'][1:]
		file_info_list = []
		for file in files:
			file_parts = file.strip(" ").split(" ")
			file_info = self.FileInfo(file_parts[0], file_parts[1], \
				file_parts[len(file_parts)-1])
			file_info_list.append(file_info)
		return file_info_list

	def version(self):
		""" 
		Returns the package version after removing the epoch part
		"""
		version = self['Version']
		epoch, sep, version = version.partition(":")
		return version or epoch
		   
	def upstream_version(self):
		""" 
		Returns the upstream version contained on the Version field
		"""                
		version_list = self.version().split("-")
		version_list.pop()        
		version = '-'.join(version_list)
		return version

	def verify_gpg(self, keyring, verbose=False):
		"""Verifies the file GPG signature using the specified keyring
		file.
		
		@param keyring: they keyring to be used for verification
		@return: the signature author or None
		"""
		gpg_cmd = "LANGUAGE=en_US.UTF-8 LANG=en_US.UTF-8 " \
		      "gpg --no-options --no-default-keyring " \
			"--keyring %s --verify --logger-fd=1 %s" \
			% (keyring, self._filename)

		sign_author = None
		(rc, output) = commands.getstatusoutput(gpg_cmd)
		output = unicode(output, 'utf-8')	
		if verbose:
			print output
		output_lines = output.split("\n")		
		if rc==0:
			for line in output_lines:		
				if line.startswith("gpg: Good signature from"):
					dummy, sign_author, dummy = line.split('"')	
		return sign_author
		
	def verify_md5sum(self, source_dir=None):
		"""
		Verify the MD5 checksum for all the files
		Returns:
			None: on success
			(expected_md5, found_md5, filename): on failure
		"""
		source_dir = source_dir or os.path.dirname(self._filename)
		for file in self.files_list():
			full_filename = "%s/%s" % (source_dir, file.name)
			if not os.path.exists(full_filename):
				return (file.md5sum, "FILE_NOT_FOUND", file.name)
			else:
				md5sum=commands.getoutput("md5sum %s" % full_filename)								
				(found_md5, dummy) = md5sum.split()
				if found_md5 != file.md5sum:
					return (file.md5sum, found_md5, file.name)
		return None	
		
	def copy(self, destination_dir=None, source_dir=None, md5check=True):
		"""
		Copies the files listed on the control file
		The control file is also copied at the end
		"""
		source_dir = source_dir or os.path.dirname(self._filename)
		if not os.path.isdir(destination_dir):
			raise Exception
			return
			
		file_list = self.files_list()
		file_list.append(self.FileInfo(None, None, \
			os.path.basename(self._filename)))
		for file in file_list:
			source_filename = "%s/%s" % (source_dir, file.name)
			target_filename = "%s/%s" % (destination_dir, file.name)
			if not os.path.exists(source_filename):
				raise self.FileNotFoundError(source_filename)
				return
			shutil.copy2(source_filename, target_filename)
			if md5check and file.md5sum:
				md5sum = commands.getoutput("md5sum %s" % target_filename)								
				(found_md5, dummy) = md5sum.split()
				if found_md5 != file.md5sum:
					raise self.MD5Error(file.md5sum, found_md5, file.name)                    
					return        
		return None

	def move(self, destination_dir=None, source_dir=None, md5check=True):
		"""
		Moves the files listed on the control file
		The control file is also moved at the end
		Returns:
			None: on success
			(expected_md5, found_md5, filename): on failure
		"""
		source_dir = source_dir or os.path.dirname(self._filename)
		if not os.path.isdir(destination_dir):
			raise Exception
			return

		file_list = self.files_list()
		file_list.append(self.FileInfo(None, None, \
			os.path.basename(self._filename)))
		for file in file_list:
			source_filename = "%s/%s" % (source_dir, file.name)
			target_filename = "%s/%s" % (destination_dir, file.name)
			if not os.path.exists(source_filename):
				raise self.FileNotFoundError(source_filename)
				return
			if os.path.exists(target_filename):
				os.unlink(target_filename)
			shutil.move(source_filename, target_filename)
			if md5check and file.md5sum:
				md5sum = commands.getoutput("md5sum %s" % target_filename)								
				(found_md5, dummy) = md5sum.split()
				if found_md5 != file.md5sum:
					raise self.MD5Error(file.md5sum, found_md5, file.name)                
					return
					
		return None

	def remove(self, source_dir=None):
		"""
		Removes all files listed and the control file itself
		Returns:
			None: on success
			(expected_md5, found_md5, filename): on failure
		"""
		source_dir = source_dir or os.path.dirname(self._filename)
		
		file_list = self.files_list()
		file_list.append(self.FileInfo(None, None, \
			os.path.basename(self._filename)))
		for file in file_list:
			full_filename = "%s/%s" % (source_dir, file.name)
			if os.path.exists(full_filename):
				os.unlink(full_filename)

	def __getitem__(self, item):
		try:
			item = self._deb_info[item]
		except KeyError:
			item = None
		return item
		
	def __str__(self):
		return `self._deb_info`

if __name__ == '__main__':
	import sys
	sample_control_file = """	
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

Format: 1.8
Date: Thu, 22 Oct 2009 14:33:27 -0300
Source: wormux
Binary: wormux wormux-data
Architecture: source
Version: 1:0.8.5-1~getdeb1
Distribution: karmic
Urgency: low
Maintainer: Debian Games Team <pkg-games-devel@lists.alioth.debian.org>
Changed-By: Emilio Zopes <turl@tuxfamily.org>
Description: 
 wormux     - funny fight game on 2D maps
 wormux-data - data files for the wormux game
Changes: 
 wormux (1:0.8.5-1~getdeb1) karmic; urgency=low
 .
   * New Upstream Version
Checksums-Sha1: 
 f3735fe3dbfb8c148f7fb55845a1c5d5c2be6f49 1722 wormux_0.8.5-1~getdeb1.dsc
 97af263126cb79abeac69472abe6f1d11f708d57 80056084 wormux_0.8.5.orig.tar.gz
 c07114ec6e5785b5453d4d8079fa815591928255 30114 wormux_0.8.5-1~getdeb1.diff.gz
Checksums-Sha256: 
 4d2404a01ef50b7c485dc5267dde09a9e243437e06d06f032d0f09c505c6cf18 1722 wormux_0.8.5-1~getdeb1.dsc
 19873f82507fd6f76ddd43278028b8e7d45281fd7a9a31099a74cbfcfc9d10cb 80056084 wormux_0.8.5.orig.tar.gz
 18cca660579abc01ac7d3ccdf4770be6532ad08fd88408ad8cd1265ec218ba8b 30114 wormux_0.8.5-1~getdeb1.diff.gz
Files: 
 84fbe8d79d9f9d555edb2f8b8dc5a5c3 1722 games optional wormux_0.8.5-1~getdeb1.dsc
 eb9eedd1018bd74d2109244bc5a84d71 80056084 games optional wormux_0.8.5.orig.tar.gz
 2f5915e1eae3655a99df202a2bb7dd07 30114 games optional wormux_0.8.5-1~getdeb1.diff.gz

-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.9 (GNU/Linux)

iEYEARECAAYFAkrgmbgACgkQ4X+nR70cqrRRgACgle7Whh7ATTH35n6KBQHGkyb0
tHIAn3lmWOuobPG1bexavbq3h36Tm7yb
=wNh8
-----END PGP SIGNATURE-----
"""
	if len(sys.argv) > 1:
		print "Parsing",sys.argv[1]
		control_file = DebianControlFile(sys.argv[1])
	else:
		control_file = DebianControlFile(contents=sample_control_file)
		#control_file.load_contents()
	print control_file
	print "------- Testing sample control file -----"
	print "Source: %s" % control_file['Source']
	print "Version: %s" % control_file.version()
	print "Upstream Version: %s" % control_file.upstream_version()
	print "Description: %s" % control_file['Description']
	if control_file.files_list():
		print "Files:"		
		for file in control_file.files_list():
			print "name: %s, size: %s, md5sum: %s" % \
				(file.name, file.size, file.md5sum)        

