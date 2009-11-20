# -*- coding: utf-8 -*-
from cherrypy_mako import *

class Logout(object):
	@cherrypy.expose
	def index(self,):		
		cherrypy.session.delete()
		cherrypy.lib.sessions.expire()
		raise cherrypy.HTTPRedirect(cherrypy.request.base+'/welcome')            		

cherrypy.root.logout = Logout()
