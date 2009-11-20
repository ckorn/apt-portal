# -*- coding: utf-8 -*-
from cherrypy_mako import *
from common.modules import sponsors
							
class Welcome(object):
	@cherrypy.expose
	
	def index(self):
		(sponsor, sponsor_total) = sponsors.get_sponsor()
		return serve_template("welcome.html", \
			sponsor = sponsor, sponsor_total = sponsor_total
		)

# set the mount point
cherrypy.root.welcome = Welcome()
