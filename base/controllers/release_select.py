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
# /release_select/ contoller
from cherrypy_mako import *

class Release_select(object):
	@cherrypy.expose
	def index(self, release = None, testing = None):
		if release:
			cherrypy.response.cookie['release'] = release
			cherrypy.response.cookie['release']['max-age'] = 86400*30
			cherrypy.response.cookie['release']['path'] = '/'
			if testing:
				cherrypy.response.cookie['testing'] = "on"
				cherrypy.response.cookie['testing']['expires'] = 86400*30
				cherrypy.response.cookie['testing']['path'] = '/'
			else:
				cherrypy.response.cookie['testing'] = "off"
				cherrypy.response.cookie['testing']['expires'] = 0
				cherrypy.response.cookie['testing']['path'] = '/'
			raise cherrypy.HTTPRedirect(cherrypy.request.base + '/welcome/')
		return serve_template("release_select.html", release = release)

cherrypy.root.release_select = Release_select()
