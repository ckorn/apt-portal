# -*- coding: utf-8 -*-
import apt_portal
from apt_portal import controller
from base.models.user import User
from base.modules import userinfo
import cherrypy

class Auth(object):
	@controller.publish
	def index(self, user = None, key = None):
		if not user or not key:
			return "Direct access is not allowed"
		user = User.query.filter_by(username = user, authkey = key).first()
		if user:
			user.auth = 1
			user.authkey = None
			userinfo.set_login_sesion_info(user)		
			apt_portal.http_redirect(apt_portal.base_url()+ "/welcome/")	
            
		return "Auth key or user are no longer valid!"

controller.attach(Auth(), "/auth") 
