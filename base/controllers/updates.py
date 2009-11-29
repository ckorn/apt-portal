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
from base.models.package import Package
from base.models.application import ApplicationsCategory
from base.modules import packages
from sqlalchemy import desc, or_, text

def updates_page(distro, release, app_name, **kwargs):
    """ Builds the updates page """
    
    try:
        page = int(kwargs.get("page", 1))
    except ValueError:
        page = 1                
    q = kwargs.get("q", None)    
    category_name = kwargs.get("category", None)
    category = None    
    categories = ApplicationsCategory.query.all() 
    if category_name:
        category = ApplicationsCategory.query.filter_by(name=category_name).first()
        if not category:
            controller.http_redirect(controller.base_url()+"/updates/ubuntu/all")
    
    (applications_list, package_dict, page_count) = \
        packages.get_applications_list(q = q, category = category, page = page 
                                        , release = release , items_per_page = 5 
                                        )
                
    # Determine the "Available for" releases 
    available_for = {}
    for app in applications_list:        
        package = Package.query.filter_by( id = package_dict[app.id].id)\
             .order_by(desc(Package.last_modified)).first()
        available_for[app.id] = {}
        available_for[app.id] = []
        for packagelist in package.lists:
            if packagelist.version not in available_for[app.id]:
                available_for[app.id].append(packagelist.version)                                
    
    search_str = controller.self_url()+"?"
    if q:
        search_str += "q=%s" % q
    if not search_str.endswith("?"):
        search_str += "&amp;"
    return template.render("updates.html"\
        , categories = categories \
        , applications_list = applications_list \
        , package_dict = package_dict \
        , available_for = available_for \
        , page = page \
        , page_count = page_count \
        , q = q \
        , category = category \
        , search_str = search_str
    )


class Updates(object):
       
    @controller.publish
    @controller.set_cache_expires(secs=0)
    def default(self, *args, **kwargs):
        """ 
        @summary: handles the following urls:
            http://base_url/updates/distribution/release/
            with the following keywords:
                q = seach keyword
                page = starting page
                category = apps from category
            Or to check the latest update for a specific releasE:
                http://base_url/updates/distribution/release/appname            
        """
        argc = len(args)
        if argc not in [2,3]:
            controller.http_redirect(controller.base_url()+"/updates/ubuntu/all")
        distro = args[0]
        release = args[1]
        app_name = None
        if argc > 3:
            app_name = args[2]

        return updates_page(distro, release, app_name, **kwargs)
        #return self.index(q = q, items_per_page = 1)


controller.attach(Updates(), "/app") 
controller.attach(Updates(), "/updates")