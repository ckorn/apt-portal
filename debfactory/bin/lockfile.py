#!/usr/bin/python
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
#  This module provides a class to work with lock files. (UNIX only)
#  

import os
import errno
import atexit


class LockFile:
    """ 
    This class simplifies the creation of lock files, to use it you 
    only need to create a LockFile object.
    Explicitely removing the lock is not required, it will be performed
    when the caller process terminates.
    """
    class AlreadyLockedError(Exception):   
        pass
                        
    def __init__(self, lock_name):
        """
        lock_name can only contain alfa numeric charaters
        """
        # Single line to reject non alfanumeric chars from name
        for x in lock_name: 
            if not (x=='_' or x.isalnum()):
                raise Exception
                return
                            
        lock_filename = "/tmp/lockfile_%s.lock" % lock_name
        # Avoid link security exploit
        #if os.path.islink(lock_filename): 
        #    print 'FATAL ERROR: symlink '+lock_filename
        #    sys.exit(2)
        oflags = os.O_RDWR |os.O_NONBLOCK| os.O_CREAT | os.O_EXCL
        
        try:
            lock_fd = os.open(lock_filename, oflags)		        
        except OSError, e:
            if e.errno == errno.EEXIST:
                raise self.AlreadyLockedError
            else:
                raise e
        else:
            atexit.register(self.release, lock_filename, \
               lock_fd)            
            os.write(lock_fd, "%d\n" % os.getpid())
            self._lock_fd = lock_fd
            self._lock_filename = lock_filename
            
    def release(self, fname=None, lock_fd=None):
        fname = fname or self._lock_filename
        lock_fd = lock_fd or self._lock_fd
        os.close(lock_fd)
        os.unlink(fname)

# Run test routines
if __name__ == '__main__':    
    try:
        print "Creating lock - #1"
        lock = LockFile("test")
        print "Done"
        print "Creating lock - #2"
        lock = LockFile("test")
        print "Done"
    except LockFile.AlreadyLockedError:
            print "Test is already locked"
            
            
    
    
