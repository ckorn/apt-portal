#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@copyright:
 
    (C) Copyright 2009, APT-Portal Developers
    https://launchpad.net/~apt-portal-devs

@license:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
@author: João Pinto <joao.pinto at getdeb.net>
"""

from apt_portal import controller
from base.models.user import User
from base.modules import userinfo

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
			controller.http_redirect(controller.base_url()+ "/welcome/")	
            
		return "Auth key or user are no longer valid!"

controller.attach(Auth(), "/auth") 
