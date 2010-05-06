#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@copyright: 

  (C) Copyright 2010, GetDeb Team - https://launchpad.net/~getdeb
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

  Test script

"""

import os
import sys
import commands
import subprocess
import time
import signal

def run_or_exit(cmd):
    print cmd,
    """ executed command with sytem(), quit script if exit code is non zero """
    (rc,output) = commands.getstatusoutput(cmd)
    if rc != 0:
        print output
        print "FAILED"
        sys.exit(rc)
    print "OK"
    
if len(sys.argv) != 2:
    print "Please provide an application name"
    sys.exit(2)
    
appname = sys.argv[1]
args = ['/usr/bin/gnome-terminal','-e','./apt-portal.py -l '+appname]
p = subprocess.Popen(args)
time.sleep(2)
run_or_exit('curl -f http://localhost:8080/welcome/')
run_or_exit('curl -f http://localhost:8080/updates/')
run_or_exit('curl -f http://localhost:8080/login/')
run_or_exit('curl -f http://localhost:8080/register/')
run_or_exit('curl -f http://localhost:8080/login/')
# Failed login case
run_or_exit('curl -f -d\"name=raxxine&password=ok&referer=xpto" http://localhost:8080/login/')
# Register
run_or_exit('curl -f -d"name=raxxine&password1=ok&password2=ok&email=local@localhost.loc"  http://localhost:8080/register/')
#os.system('./apt-portal.py '+appname+' stop')
#p.send_signal(signal.SIGHUP)
