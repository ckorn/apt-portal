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

import cherrypy
from apt_portal import database
from base.models.package import Package, PackageList
from base.models.application import Application

def get_applications_list(q, category, release, page = 1, items_per_page = 10):
    """
    @summary: Returns a list of packages and the associated applications
    
    @param q: search keyword string (to be matched with app names and short descriptions)
    @param exact_search: flag to enable/disable exact search 
        if enabled search only for app name == q or package name == q
    @param category: category (a Category DB entity)
    @param items_per_page: max number of applications to be returned
    @param page: page number to be used as the initial row offset (page*limit)  
    @return: (app_list, package_dict, data_count)
        app_list : list of applications (Application db entity)
        app_dict: dict containing the package information for packages related 
            to the app_list.  The application id is the dict key.
        page_count : total number of pages, useful for pagination
    """
    if page < 0:
        page = 1
        
    # First we need to determine the ids for package lists matching the release
    # selection filter
    if not release or release == "all":
        packagelists = PackageList.query.all()
    else:
        packagelists = PackageList.query.filter_by(version = release).all()
    packagelist_ids = []
    for plist in packagelists:
        if plist.suite.endswith('-testing'):
            continue
        packagelist_ids.append(str(plist.id))
    if len(packagelist_ids) == 0: # an empty db
        return ([], {}, 0)
    selected_plists = ' ,'.join(packagelist_ids)
    sql_args = {}
    
    # We will use a 2 steps process to identify the list of packages/apps that
    # that will be returned
    
    # STEP 1 - Get list of apps with updates matching the search criteria
    # Get the list of main packages name and and related applications ids
    # ordered with newer packages (last modified) on the top
    sql_select_count = "SELECT COUNT(DISTINCT application.id) "
    sql_select_data = "SELECT DISTINCT application.id, package "
    sql_where = " WHERE package.install_class='M' "    
    sql_join_where = "(application.source_package = package.package OR application.source_package = package.source)"
    sql_limit = " LIMIT :limit OFFSET :offset"
    sql_args['limit'] = int(items_per_page)
    sql_args['offset'] = (page - 1) * items_per_page
    match_operator = 'LIKE'   
    if q: # a search keyword was specified
        sql_where += ' AND (package.package '+match_operator+' (:q)'
        sql_where += ' OR application.name '+match_operator+' (:q)'
        sql_where += ' OR package.description '+match_operator+' (:q)'
        sql_where += ')';            
        sql_args['q'] = '%'+q+'%'
    elif category: # a category was specified
        sql_join_where += " AND application.category_id=:category_id"
        sql_args['category_id'] = category.id            
    sql_body = \
    " FROM package" \
    " INNER JOIN application ON (" +sql_join_where +")" \
     + sql_where +\
    " AND package.id IN (SELECT package_id FROM packagelist_members WHERE packagelist_id IN (%s)) " % selected_plists
    sql_order = " ORDER BY last_modified DESC "
    engine = database.engine()
    count_sql = engine.text(sql_select_count+sql_body)
    select_sql = engine.text(sql_select_data+sql_body+sql_order+sql_limit)                
    row_count = count_sql.execute(**sql_args).fetchone()[0]
    if row_count == 0: # nothing found
        return ([], {}, 0) 
    data = select_sql.execute(**sql_args).fetchall()
        
    # STEP 2 - Get specific version and application records for apps/packages
    # listed on STEP 1
    
    # We already have apps ids/packages names, now we need to get specific 
    # package and application records  
    app_list = []
    package_dict = {}
    for item in data:
        sql = "SELECT id FROM package WHERE package = :pck_name "
        sql +=  "AND package.id IN (SELECT package_id FROM packagelist_members WHERE packagelist_id IN (%s)) " % selected_plists
        sql += " ORDER BY last_modified DESC LIMIT 1 "
        specific_sql = engine.text(sql)         
        package = specific_sql.execute(pck_name = item.package).fetchone()
        if not package: # Package was deleted ????
            continue
        package_id = package.id
        app = Application.query.filter_by(id = item.id).first()
        if not app: # App was deleted ?
            continue        
        package = Package.query.filter_by(id = package_id).first()
        if not package:
            continue
        app_list.append(app)
        package_dict[app.id] = package
    page_count = ((row_count - 1) / items_per_page) + 1
    return (app_list, package_dict, page_count)
