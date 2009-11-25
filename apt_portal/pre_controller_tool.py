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
# The precontroller tool is used for the foollowing tasks:
#	Based on the user agent string:
#		Set cherrypy.request.user_distro_name  variable
#		Set cherrypy.request.user_distro_version
#	Based on the release cookie and cherrypy.request.user_distro_version
#		Set cherrypy.request.release
import cherrypy
import re

def precontroller():
	
	# static resources are not under precontroller control
	if cherrypy.request.config.get('tools.staticdir.on', False) or \
		cherrypy.request.config.get('tools.staticfile.on', False):
			return
	
	release = None
	cherrypy.request.user_distro_name = None
	cherrypy.request.user_distro_version = None
	user_agent = cherrypy.request.headers.get('User-Agent', None)
	
	if user_agent:
		find_distro = re.findall('(Ubuntu)/([\d\.]*)', user_agent)
		if find_distro:
			cherrypy.request.user_distro_name = find_distro[0][0]
			cherrypy.request.user_distro_version = find_distro[0][1]
	cherrypy.request.release = None			
	
	try:
		release = cherrypy.request.cookie["release"].value	
	except KeyError:
		pass
		
	if not release and cherrypy.request.user_distro_version:
		release = cherrypy.request.user_distro_version 
	
	if release not in ['9.04', '9.10', '10.04', '10.10']:
		release = "all"
	cherrypy.request.release = release		
	
cherrypy.tools.precontroller = cherrypy.Tool('on_start_resource', precontroller)
