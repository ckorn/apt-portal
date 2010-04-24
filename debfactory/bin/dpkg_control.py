#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
  (C) Copyright 2009, GetDeb Team - https://launchpad.net/~getdeb
  --------------------------------------------------------------------
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
  --------------------------------------------------------------------

  This file provides several functions to handle debian packages
  control files.
"""

import sys
import os
import commands     # We need it for the GPG signature verification
import shutil
import types
from apt_pkg import TagFile

class DebianControlFile(object):
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
    
    
    def __init__(self, input=None):
        
        if type(input) == types.StringType:
            self._filename = input
            self.load(input)
        else:
            self.tagfile = TagFile(input)        
            
    def load(self, input):
        """
        Load control file
        """
        plain_file = open(input)
        tagfile = TagFile(plain_file)
        
        # Loop to skip PGP signature
        while tagfile.step():
            if tagfile.section.keys()[0][0] != '-':
                break

        self.tagfile = tagfile
    
    def step(self):
        """ Advance to next section """
        return self.tagfile.step()
        
    def files_list(self):
        if not self['Files']:
            return None
        files = self['Files'].split('\n')
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
        version = self.tagfile.section['Version']
        epoch, sep, version = version.partition(":")
        return version or epoch
    
    def upstream_version(self):
        """ 
        Returns the upstream version contained on the Version field
        """          
        return self.version().rsplit("-", 1)[0]  

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
                md5sum = commands.getoutput("md5sum %s" % full_filename)                                
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
            item = self.tagfile.section[item]
        except KeyError:
            item = None
        return item
        
    def __str__(self):
        return str(self.tagfile.section)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "You must supply a filename for testing"
        sys.exit(1)        
    print "Parsing",sys.argv[1]
    control_file = DebianControlFile(sys.argv[1])
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

