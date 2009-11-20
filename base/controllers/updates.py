# -*- coding: utf-8 -*-
#
#   (C) Copyright 2009, APT-Portal Developers
#    https://launchpad.net/~apt-portal-devs
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from cherrypy_mako import *
from sqlalchemy import desc
from models.package import *
from models.application import *
from sqlalchemy import or_, text

def get_list_of_packages(q, exact_search, cat, limit = 10, page = 1):
	"""
	This functions builds a SQL to get the package names that will be
	shown.
	returns a tuple, (list_of_packages, page count)
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
		engine = metadata.bind
		count_sql = engine.text(sql_count+sql_body)
		select_sql = engine.text(sql_select+sql_body+sql_order+sql_limit)				
#		print select_sql, sql_args		
		
#		print engine
		# sqlite does not support SELECT COUNT(DISTINC(a,b))
#		if engine.url.drivername == "sqlite":
#			count = len(select_sql.execute(**sql_args).fetchall())
#		else:
#			print count_sql, sql_args
		count = count_sql.execute(**sql_args).fetchone()[0]
		data = select_sql.execute(**sql_args).fetchall()
#		print "count=", count
#		print "data=", data
		try_count -= 1
		# if not found try searching for app name
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
		
class Updates(object):
	@cherrypy.expose
	@cherrypy.tools.expires(secs=0)
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
		packages_info = get_list_of_packages(\
			q = q, cat = cat, exact_search = exact_search, page = page \
			, limit = items_per_page \
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
		
		search_str = cherrypy.request.path_info+"?"
		if q:
			search_str += "q=%s" % q
		if testing:
			if not search_str.endswith("?"):
				search_str += "&amp;"
			search_str += "testing=Y"
		if not search_str.endswith("?"):
			search_str += "&amp;"
		return serve_template("updates.html"\
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
		
	@cherrypy.expose
	@cherrypy.tools.expires(secs=0)
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
	
	@cherrypy.expose
	@cherrypy.tools.expires(secs=0)	
	def default(self, *args):
		if len(args) < 1:
			raise cherrypy.HTTPRedirect('.')
						
		exact_search = args[0]
		return self.index(exact_search = exact_search)


cherrypy.root.updates = Updates()
cherrypy.root.app = cherrypy.root.updates # Keep old getdeb link available
