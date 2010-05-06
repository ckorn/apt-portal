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

from apt_portal import controller, template
from base.models.user import User
from base.modules import userinfo
    
class Login(object):
    @controller.publish
    def index(self, name=None, password = None, referer=None):
        if name: # submitting
            user = User.query.filter_by(username = name).first()
            if user and user.password == userinfo.md5pass(password, user.password):
                if user.auth == 1:
                    userinfo.set_login_sesion_info(user)
                    if referer:
                        controller.http_redirect(referer)
                    else:
                        controller.http_redirect(controller.base_url()+'/welcome/')
                else:
                    return template.render("login.html" 
                        , error_reason = "auth" 
                        , referer = referer 
                        )                    
            else:                
                return template.render("login.html"
                    , error_reason = "failed" 
                    , referer = referer 
                    )
        else:
            referer = controller.get_header('Referer')
            if not referer:
                referer = controller.base_url()+"/welcome/"
            return template.render("login.html"
                , hide_login_register = True
                , referer = referer
                , error_reason = None)
                
controller.attach(Login(), "/login")
