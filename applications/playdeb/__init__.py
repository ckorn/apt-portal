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

import apt_portal

print "Loading PlayDeb Application controllers"

apt_portal.set_app_static_dirs(['css', 'images', 'js'])

# base controllers
import base.controllers.about
import base.controllers.error_404
import base.controllers.welcome
import base.controllers.register 
import base.controllers.auth
import base.controllers.login
import base.controllers.logout
import base.controllers.updates
import base.controllers.contact
import base.controllers.sponsors
import base.controllers.install
import base.controllers.software

# Admin only
import base.controllers.packages
import base.controllers.appinfo
