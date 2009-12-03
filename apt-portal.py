#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@copyright:
 
    (C) Copyright 2009, APT-Portal Developers
    https://launchpad.net/~apt-portal-devs

@license:
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
    
@author: João Pinto <joao.pinto at getdeb.net>

     This is the application manager script
     
"""

import warnings
import sys
import os
import tempfile

import apt_portal
from apt_portal import database, main

# suppress the deprecation warning in elixir 0.6.1 import warnings 
warnings.simplefilter('ignore', DeprecationWarning, 412) # 

# Setup 

""" Main code """
if __name__ == '__main__':       	
    run_on_foreground = False
          
    # Get the command line options
    (options, args) = main.command_line_parser().parse_args()
    if len(args) < 1:
    	print "Usage: %s app_name [cmd] [options]" % os.path.basename(__file__)
    	sys.exit(2)
    	
    app_name = args[0]
    appcmd = None
        
    if len(args) > 1:
    	appcmd = args[1]
    	
    if options.console_log or options.no_fork or options.sql_echo:
    	run_on_foreground = True
       
    # Check if there is an application on the expected directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(os.path.join(base_dir, "applications" \
    	, app_name)):
    	print "No application %s on the applications directory" \
    		% app_name
    	sys.exit(3)
    	
    # Set the database engine here
    db_url = options.database 
    if not db_url:
        db_path = os.path.join(os.environ['HOME'], "."+app_name)+".db"		
        db_url = "sqlite:///" + db_path
        print "No database specified, using sqlite3 db", db_path 
    
    # stdin is a special url which prompts for the database url
    # this allows to start the process without having the url included
    # on the system command startup arguments
    if db_url == 'stdin': # special case to request from stdin (secure)
        db_url = raw_input('Please enter the db url:')
        print
    
    database.setup(db_url, options.sql_echo)
    
       # Handle --add-admin
    if options.add_admin:
    	rc = main.add_admin(options.add_admin)
    	sys.exit(rc)
    
    is_running = apt_portal.is_running(app_name)
    if appcmd in ("stop", "restart"): # Stop running application
    	if is_running:						
    		apt_portal.stop(app_name)
    	if appcmd == "stop": 
    		sys.exit(0)
    		
    # Check again - application could still be running
    is_running = apt_portal.is_running(app_name)		
    if is_running:
    	print "The application is already running with pid", is_running
    	print "You can't run multiple instances of the same application"
    	sys.exit(2)
    				
    # Set the app server configuration	
    apt_portal.set_default_config(app_name, options)	
    	
    # Set directories for the templating engine
    app_dir = os.path.join(base_dir, 'applications', app_name)
    apt_portal.template.set_directories(
    	[os.path.join(app_dir,'views') \
    		, os.path.join(base_dir, 'base', 'views') \
    	] \
    	, os.path.join(tempfile.mkdtemp())
    	)
    
    if options.force_view:
    	apt_portal.force_root(options.force_view)
    	print "Forcing the template to", options.force_View
    else: # regular startup                   
    	app_startup_module = os.path.join(app_dir, 'startup.py')
    	exec("import applications."+app_name)
    
    apt_portal.start(run_on_foreground)
    	
