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
from apt_portal import controller, template
from sqlalchemy import desc, or_, text
from base.models.package import Package
from base.models.application import Application, ApplicationsCategory
from base.modules import packages

		
class Updates(object):
	@controller.publish
	@controller.set_cache_expires(secs=0)
	def index(self, page = 1, q = None, category = None, \
		testing = None, exact_search = None):
		items_per_page = 5
		cat = None
		try:		
			page = int(page)
		except ValueError:
			page = 1
		app_list = {} # keep list of apps related to packages
		app_extra_info = {} # app  extra information
		visible_packages_list = []
		categories = ApplicationsCategory.query.all() 
		if category:
			cat = ApplicationsCategory.query.filter_by(name=category).first()
			if not cat:
				raise cherrypy.HTTPRedirect('.')
		packages_info = packages.get_applications_list(
			q = q, cat = cat, exact_search = exact_search, page = page 
			, limit = items_per_page 
			)
		page_count = ((packages_info[0] - 1) / items_per_page) + 1
		packages_to_show = []				
		for package_info in packages_info[1]:			
			package = Package.query.filter_by( id = package_info[0])\
			     .order_by(desc(Package.last_modified)).first()
			app = Application.query.filter_by(id = package_info[1]).first()
			if not (package or app): # Package or app was deleted after query ?
				continue
			packages_to_show.append(package)
			app_key = package.package+package.version
			app_extra_info[app_key] = {}
			app_extra_info[app_key]['releases'] = []
			#app_extra_info[app_key]['only_on_testing'] = only_on_testing
			for package_list in package.lists:
				if package_list.version not in app_extra_info[app_key]['releases']:
					app_extra_info[app_key]['releases'].append(package_list.version)				
			app_list[app_key] = app
		
		search_str = controller.self_url()+"?"
		if q:
			search_str += "q=%s" % q
		if testing:
			if not search_str.endswith("?"):
				search_str += "&amp;"
			search_str += "testing=Y"
		if not search_str.endswith("?"):
			search_str += "&amp;"
		return template.render("updates.html"\
			, categories = categories \
			, app_list = app_list \
			, app_extra_info = app_extra_info \
			, packages_to_show = packages_to_show \
			, page = page \
			, page_count = page_count \
			, q = q \
			, cat = cat \
			, search_str = search_str \
			, testing = testing \
		)
		
	@controller.publish
	@controller.set_cache_expires(secs=0)
	def category(self, *args, **vars):
		if len(args) != 1:
			raise cherrypy.HTTPRedirect('.')
		category = args[0]
		page = vars.get('page', 1)
		q = vars.get('q', None)
		testing = vars.get('testing', None)
		return self.index(page = page, q = q, category = category \
			, testing = testing \
			)
	
	@controller.publish
	@controller.set_cache_expires(secs=0)
	def default(self, *args):
		if len(args) < 1:
			raise cherrypy.HTTPRedirect('.')
						
		exact_search = args[0]
		return self.index(exact_search = exact_search)


controller.attach(Updates(), "/app") 
controller.attach(Updates(), "/updates")
 
