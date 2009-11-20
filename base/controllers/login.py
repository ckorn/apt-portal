# -*- coding: utf-8 -*-
from cherrypy_mako import *
from models.user import *
import userinfo
	
class Login(object):
	@cherrypy.expose
	def index(self, password = None, referer = None, name =None, 
		submitting = None):
		if submitting:
			user = User.query.filter_by(username = name\
			, password = userinfo.md5pass(password)).first()
			if user:
				if user.auth == 1:
					userinfo.set_login_sesion_info(user)
					if referer and pagename not in  ["register"]:
						raise cherrypy.HTTPRedirect(referer)
					else:
						raise cherrypy.HTTPRedirect('./welcome/')
				else:
					return serve_template("login.html" \
						, error_reason = "auth" \
						, referer = referer \
						)                    
			else:                
				return serve_template("login.html" \
					, error_reason = "failed" \
					, referer = referer \
					)
		else:
			referer = None
			if 'Referer' in cherrypy.request.headers:
				referer = cherrypy.request.headers['Referer']
			else:
				referer = cherrypy.request.base+"/welcome/"
			return serve_template("login.html" \
				, hide_login_register = True \
				, referer = referer \
				,  error_reason = None)
				
cherrypy.root.login = Login()
