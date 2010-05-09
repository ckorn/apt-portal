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
from base.models.application import Application
from base.models.package import Package, PackageList
from sqlalchemy import and_, or_, desc

class Software(object):
    @controller.publish
    def default(self, *args):
        if len(args) < 1:
            controller.http_redirect(controller.base_url())
        app_name = args[0].replace('+',' ')        
        application = Application.query.filter_by(name = app_name).first()
        if not application:
            application = Application.query.filter_by(\
                source_package = app_name).first()
        if not application:
            controller.http_redirect(controller.base_url())            
            
        # Get dict of the latest version for each distro release
        last_version_dict = {}        
        last_package = None    
        for plist in PackageList.query.all():
            if plist.suite.endswith('-testing'):
                continue
            package = Package.query.filter(and_(Package.lists.any(id=plist.id), 
                or_(Package.package==application.source_package, Package.source==application.source_package),
                Package.install_class=='M'))\
                .order_by(desc(Package.last_modified)).first()
            if package:
                last_version_dict[plist.version] = package.version
                last_package = package  
        return template.render("software.html", app=application,
                               last_version_dict=last_version_dict, 
                               package=last_package)
    
controller.attach(Software(), "/app") 
controller.attach(Software(), "/software") 
