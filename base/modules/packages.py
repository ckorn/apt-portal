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
from base.models.package import PackageList

def get_applications_list(q, exact_search, cat, limit = 10, page = 1):
    """
    @param q: query text (will be matched with app names and short descriptions)
    @param exact_search: flag to enable/disable exact search 
        if enabled search only for app name == q or package name == q
    @param cat: category filter (a Category DB entity)
    @param limit: max number of limits to return
    @param page: page number to be used as the initial row offset (page*limit)  
    @return: (packages_count, data_count)
        packages_count : number of entries matching the selection criteria
        packages_data : list with (package_info, app_info)
            package_info : package information (Package db entity)
            application_info: application information (Application db entity)            
    @note: 
        package_count maybe > len(packages_data) because limits are not applied
    """
    if page < 0:
        page = 1
    try_count = 1
    release = cherrypy.request.release
    try:
        show_testing = cherrypy.request.cookie["testing"].value    
    except KeyError:
        show_testing = None    
    if not release or release == "all":
        packagelists = PackageList.query.all()
    else:
        packagelists = PackageList.query.filter_by(version = release).all()
    packagelist_ids = []
    for plist in packagelists:
        if show_testing != "on" and plist.suite.endswith('-testing'):
            continue
        packagelist_ids.append(str(plist.id))
    if len(packagelist_ids) == 0: # an empty db
        return (0, [])
    selected_plists = ' ,'.join(packagelist_ids)
    sql_args = {}
    sql_count = "SELECT COUNT(DISTINCT application.id) "
    sql_select = "SELECT DISTINCT application.id, package"
    sql_where = " WHERE package.install_class='M' "    
    sql_join_where = "(application.source_package = package.package OR application.source_package = package.source)"
    sql_limit = " LIMIT :limit OFFSET :offset"
    sql_args['limit'] = limit
    sql_args['offset'] = (page - 1) * limit
    if q:
        sql_where += " AND (package.package LIKE (:q) OR package.description LIKE (:q))"
        sql_args['q'] = '%'+q+'%'
    elif cat:
        sql_join_where += " AND application.category_id=:category_id"
        sql_args['category_id'] = cat.id
    elif exact_search:
        sql_where += " AND package.package = :exact_search"
        sql_args['exact_search'] = exact_search    
        try_count = 2
    while try_count > 0:
        sql_body = \
        " FROM package" \
        " INNER JOIN application ON (" +sql_join_where +")" \
         + sql_where +\
        " AND package.id IN (SELECT package_id FROM packagelist_members WHERE packagelist_id IN (%s)) " % selected_plists
        sql_order = " ORDER BY last_modified DESC "
        engine = database.engine()
        count_sql = engine.text(sql_count+sql_body)
        select_sql = engine.text(sql_select+sql_body+sql_order+sql_limit)                
        count = count_sql.execute(**sql_args).fetchone()[0]
        data = select_sql.execute(**sql_args).fetchall()
        try_count -= 1
        # if not found try searching by app name
        if exact_search and try_count > 0:
            if count == 0:
                sql_where = " WHERE package.install_class='M' "    
                sql_join_where += " AND application.name = :exact_search"
                sql_body = \
                " FROM package" \
                " INNER JOIN application ON (" +sql_join_where +")" \
                 + sql_where +\
                " AND package.id IN (SELECT package_id FROM packagelist_members WHERE packagelist_id IN (%s)) " % selected_plists
                sql_order = " ORDER BY last_modified DESC "                
            else:
                try_count -= 1
    # We need this extra loop to obtain the package ids for the versions
    # that are visible
    new_data_list = []
    for item in data:
        sql = "SELECT id FROM package WHERE package = :pck_name "
        sql +=  "AND package.id IN (SELECT package_id FROM packagelist_members WHERE packagelist_id IN (%s)) " % selected_plists
        sql += " ORDER BY last_modified DESC LIMIT 1 "
        specific_sql = engine.text(sql)         
        pck_info = specific_sql.execute(pck_name = item.package).fetchone()
        if not pck_info: # Package was deleted ????
            continue
        new_data = (pck_info.id, item.id)
        new_data_list.append(new_data)
    return (count, new_data_list)
