# -*- coding: utf-8 -*-
from cherrypy_mako import *
from models.user import *
import userinfo

class Auth(object):
	@cherrypy.expose
	def index(self, user = None, key = None):
		if not user or not key:
			return "Direct access is not allowed"
		user = User.query.filter_by(username = user, authkey = key).first()
		if user:
			user.auth = 1
			user.authkey = None
			session.commit()
			userinfo.set_login_sesion_info(user)			
			raise cherrypy.HTTPRedirect(cherrypy.request.base + '/welcome/')            
		return "Auth key or user are no longer valid!"

cherrypy.root.auth = Auth()
