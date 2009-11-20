# -*- coding: utf-8 -*-
from cherrypy_mako import *

							
class Welcome(object):
	@cherrypy.expose
	def index(self):
		return serve_template("welcome.html")

# set the mount point
cherrypy.root.welcome = Welcome()








