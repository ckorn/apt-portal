#!/usr/bin/python
#
#    (C) Copyright 2009, GetDeb Team - https://launchpad.net/~getdeb
#    --------------------------------------------------------------------
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    --------------------------------------------------------------------
"""
Local auxiliar functions library
"""
import os
import sys
import commands
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

import smtplib
import atexit
import time

def uniq(alist):
    set = {}
    return [set.setdefault(e,e) for e in alist if e not in set]

""" Small helper class for logging """
class Logger:
    def __init__(self, verbose=True):
        self.verbose = verbose
        
    def log(self, message, verbose=None):
        """
        If verbose is True print the message
        """
        verbose = verbose or self.verbose
        if self.verbose:
            print "%s: %s" % (time.strftime('%c'), message)
            
    def print_(self, message):
        """
        always print a message
        """
        print "%s: %s" % (time.strftime('%c'), message)
		
def check_md5sum(filename, expected_md5sum):
	"""
	"""
	md5sum=commands.getoutput('md5sum '+filename)
	(newmd5, dummy) = md5sum.split()
	#newmd5 = newmd5.strip('\r\n')
	if newmd5 != expected_md5sum:     	
		return newmd5
	return None

def send_email(toaddrs, message):
    fromaddr = '"GetDeb Automated Builder" <autobuild@getdeb.net>'
    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, toaddrs, message)
    server.quit()
	
def send_mail_message(destination, subject, body):
    """
    Sends a mail message
    """
    
    if type(destination) is list:        
        destination = uniq(destination)
        for dest in destination:
            message = "Subject: %s\n" % subject            
            message += "To: %s\n" % dest
            message += "\n\n"
            message += body            
            send_email(dest, message)		
    else:
        send_email(destination, message)		
