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
import time
import apt_portal
from apt_portal import controller, template
from base.modules import userinfo

class Contact(object):
    @controller.publish
    def index(self, name = None, email = None, comment = None):
        if not name:
            return template.render("contact.html")
        # server side input validation
        if not email:
            return "Email is missing"
        if not comment or len(comment)<10:
            return "Comment is missing"
        if not userinfo.validateEmail(email):            
            return "Invalid email"  
        referer = controller.get_header('Referer')
        if not referer or not referer.startswith(controller.base_url()):
            return "Not Allowed"		
        contact_recipient = apt_portal.get_config("mail", "contact_recipient")
        id = int(time.time())
        template.sendmail('contact.mail'\
    		, sender = '"%s" <%s>' % (name, email)
    		, destination = contact_recipient
    		, comment = comment
            , app_name = apt_portal.app_name
            , id = id
    	)  
        return template.render("contact.html", contact_received=1)

controller.attach(Contact(), "/contact") 
