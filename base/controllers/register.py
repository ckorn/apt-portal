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

	/register/ controller
	User registration form
"""
import apt_portal   # we need get_config
from datetime import datetime
from apt_portal import controller, template
from base.models.user import User
from base.modules import userinfo

class Register_View(object):

    @controller.publish
    def index(self, name=None, email=None, password1=None, password2=None):
        if not name:
            return template.render("register.html")
        # Server side validation
        if not userinfo.validateUsername(name):
            return "Invalid username"		
        if not email:
            return "Email is missing"
        if not password1:
            return "Password is missing"            
        if not userinfo.validateEmail(email): 
            return "Invalid email"

        if User.query.filter_by(username = name).first():
            return template.render("register.html" \
        		, user_already_exists=True, submit=True)
        
        if User.query.filter_by(email = email).first():
            return serve_template("register.html" \
        	, user_email_exists=True, submit=True)        
        authkey = userinfo.generate_auth_key()
        password = userinfo.md5pass(password1)
        # Clean the password fields - security
        password1 = None
        password2 = None
        # Insert the new user
        new_user = User(\
        	username = name, \
        	email = email, \
        	password = password, \
        	authkey = authkey, \
        	auth = 0, \
        	t_register = datetime.now(), \
        	t_login = datetime.now(), \
        	t_seen = datetime.now() )
        sender = apt_portal.get_config("mail", "register_sender")
        template.sendmail("register.mail" \
        	, sender = sender \
        	, destination = email \
        	, username = name \
        	, authkey = authkey \
        	, sitename = "localhost" \
        )
        return template.render("register.html", submit=True)

controller.attach(Register_View(), "/register") 
