#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@copyright:
 
    (C) Copyright 2009-2010, APT-Portal Developers
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
from base.modules import packages, distroinfo
from sqlalchemy import desc

def updates_page(distro, release, **kwargs):
    """ Builds the updates page """
    
    try:
        page = int(kwargs.get("page", 1))
    except ValueError:
        page = 1
    updates_release = release                        
    q = kwargs.get("q", None)    
    category_name = kwargs.get("category", None)
    format = kwargs.get("format", None)
    category = None    
    categories = ApplicationsCategory.query.all() 
    if category_name:
        category = ApplicationsCategory.query.filter_by(name=category_name).first()
        if not category:
            controller.http_redirect(controller.base_url()+"/updates/Ubuntu/" + \
                controller.current_release)
    codename = distroinfo.get_codename(distro, release) 
    if format == "xml":
        items_per_page = 100
    else:
        items_per_page = 5
    (applications_list, package_dict, page_count) = \
        packages.get_applications_list(q = q, category = category, page = page 
                                        , release = release , items_per_page = items_per_page
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
    
    # Build the changelogs urls
    changelogs_dict ={}
    for app in applications_list:        
        package = Package.query.filter_by( id = package_dict[app.id].id)\
             .order_by(desc(Package.last_modified)).first()
        source_package = package.source or package.package             
        if source_package[:3] == 'lib':
            prefix = source_package[:4]
        else:
            prefix = source_package[:1]
        
        changelogs_dict[app.id] = '%s/%s/%s_%s_source.changelog' % \
            (prefix, source_package, source_package, package.version)                            
    
    search_str = controller.self_url()+"?"
    param_str = ''
    for key,value in kwargs.iteritems():
        if key == "page": 
            continue        
        param_str += key + '=' + value + '&amp;'
    if param_str:
        search_str = controller.self_url()+ '?' + param_str
    if format == "xml":
        return template.render('updates.xml' 
            , applications_list = applications_list
            , package_dict = package_dict 
            , available_for = available_for    
            , updates_release = updates_release 
            , changelogs_dict = changelogs_dict                    
        )
    else: 
        return template.render('updates.html'
            , categories = categories 
            , applications_list = applications_list 
            , package_dict = package_dict 
            , available_for = available_for 
            , page = page 
            , page_count = page_count 
            , q = q 
            , category = category 
            , search_str = search_str
            , updates_release = updates_release
            , codename = codename
            , changelogs_dict = changelogs_dict
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
        if argc != 2:
            controller.http_redirect(controller.base_url()+"/updates/Ubuntu/"\
                                     +controller.current_release)
        distro = args[0]
        release = args[1]

        return updates_page(distro, release, **kwargs)


controller.attach(Updates(), "/updates")