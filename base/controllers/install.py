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
# /install/(appname) contoller

from cherrypy_mako import *



class Install:
	@cherrypy.expose
	def default(self, *args):
		ubuntu_version = None
		if len(args) < 1:
			return "Invalid parameter count"
		pck_name = args[0]
		if len(args) > 1:
			pck_version = args[1]
		return serve_template("install.html", package_name = pck_name)		

cherrypy.root.install = Install()

