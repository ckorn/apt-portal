#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   (C) Copyright 2009, APT-Portal Developers
#    https://launchpad.net/~apt-portal-devs
#
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
#

# This is the main script

import sys
import os
import tempfile
import signal
import time
from optparse import OptionParser

import cherrypy
from cherrypy.process import plugins, servers
from cherrypy.lib import cptools

# Setup 
import apt_portal
from apt_portal import database
"""
	Set the access logs to be rotated when they reach rot_maxBytes
	keeping a max of rot_backupCount log files
"""

 

	
	
""" Add an username to the admin group """
def add_admin(username):
		from models.user import User, UsersGroup
		admin_group = UsersGroup.query.filter_by(name = "Admin").first()
		if not admin_group: # if not found create it
			admin_group = UsersGroup(name = "Admin")
		user = User.query.filter_by(username = username).first()
		if not user:
			print "User %s is not registed" % username
			return 2
		if admin_group in user.groups:
			print "User %s is already on the admin group." \
				% username
			return 1
		else: # add it
			user.groups.append(admin_group)		
			user.auth = 1
			session.commit()
			print "User %s added to the admin group." \
				% username
		return 0

""" 
	Returns an option parser object with the available 
	command line parameters
"""	
def command_line_parser():
	parser = OptionParser()
	parser.add_option("-a", "--add-admin",
		action = "store", type="string", dest="add_admin",
		help = "Add an user to the admin group" \
		)        				
	parser.add_option("-b", "--bindip", \
		action = "store", type="string", dest="host", \
		help = "set bind address for the listener (default=127.0.0.1)" \
		, default="127.0.0.1")
	parser.add_option("-d", "--database",
		action = "store", type="string", dest="database",
		help = "specificy the database URI\n\n" \
		"Examples\n\n" \
		"   mysql://user:password@localhost/database" \
		"   sqlite:///database" \
		)        
	parser.add_option("-e", "--daemon", \
		action = "store_true", dest="daemon", default=False, \
		help = "run process as a daemon (background)")		
	parser.add_option("-f", "--force-view", \
		action = "store", type="string", dest="force_view", \
		help = "force a specific view to be server for all requests\n" \
			"Usefull if you need to provide a maintenance warning")
	parser.add_option("-l", "--console-log", \
		action = "store_true", dest="console_log", default=False, \
		help = "print the http log to the console")
	parser.add_option("-p", "--port", \
		action = "store", type="string", dest="port", \
		help = "set bind address for the listener (default=8080)" \
			, default="8080" )                  
	parser.add_option("-s", "--sql-echo", \
		action = "store_true", dest="sql_echo", default=False, \
		help = "echo the sql statements")
	return parser


""" Main code """
if __name__ == '__main__':   
 
	running_pid = None
	run_on_foreground = False
	cherrypy.base_dir = base_dir = os.path.dirname(os.path.abspath(__file__))

	# We need this for common models import
	#commons_dir = os.path.join(base_dir, 'common')
	#if not commons_dir in sys.path:
	#	sys.path.insert(0, commons_dir)            
    
    # Get the command line options
	(options, args) = command_line_parser().parse_args()
	if len(args) < 1:
		print "Usage: %s app_name [cmd] [options]" % os.path.basename(__file__)
		sys.exit(2)
		
	app_name = args[0]
	pid_dir = os.path.join(base_dir, 'var', 'run')		
	pid_file = os.path.join(pid_dir, app_name+'.pid')
	appcmd = None
	
	if len(args) > 1:
		appcmd = args[1]
		
	# Check if there is a running pid
	try:
		f = open(pid_file, 'r')
	except IOError: # Unable to open
		pass
	else:
		running_pid = int(f.readline())
		f.close()
			
	if appcmd in ("stop", "restart"): # Stop running application
		if running_pid:			
			print "Killing PID", running_pid
			try:
				os.kill(running_pid, signal.SIGTERM)
			except OSError: # No such process
				print "Process is not running"
				os.unlink(pid_file)
		if appcmd == "stop": 
			sys.exit(0)
		else: # restart
			time.sleep(2)
		
	if options.console_log:
		run_on_foreground = True
    
	# Check if there is an application on the expected directory
	if not os.path.isdir(os.path.join(base_dir, "applications" \
		, app_name)):
		print "No application %s on the applications directory" \
			% app_name
		sys.exit(3)
		
	# We set the database engine here
	db_url = options.database 
	if not db_url:
		db_path = os.path.join(os.environ['HOME'], "."+app_name)		
		db_url = "sqlite:////%s.db" % db_path
		print "No database name specified, using", db_url 
	
	# stdin is a special url which prompts for the database url
	# this allows to start the process without having the url included
	# on the system command startup arguments
	if db_url == 'stdin': # special case to request from stdin (secure)
		db_url = raw_input('Please enter the db url:')
		print
	
	database.setup(db_url, options.sql_echo)

    # Handle --add-admin
	if options.add_admin:
		rc = add_admin(options.add_admin)
		sys.exit(rc)
		
	if running_pid:
		try:
			is_running = not os.kill(running_pid, 0)
		except OSError:
			is_running = False
		if is_running:
			print "The application is already running with pid", running_pid
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
	
	
	# Set the web root handler
	# If the force view parameter is used then we need to use a special
	# web root controlller which handles web_root/* unlike the regular
	if options.force_view:
		apt_portal.force_root(options.force_view)
		print "Forcing the template to", options.force_View
	else:                   
		app_startup_module = os.path.join(app_dir, 'startup.py')
		if os.path.exists(app_startup_module):		
			sys.path.insert(0, app_dir)
			import startup
			sys.path.remove(app_dir)
		
	apt_portal.merge_config(os.path.join(base_dir, 'applications' \
		, app_name, 'config', 'base.conf'))
	
	
	apt_portal.start(run_on_foreground)
		
