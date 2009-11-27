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

import os
import time
import apt_portal
from apt_portal import controller, template
from sqlalchemy import asc
from base.modules import userinfo
from base.models.application import Application
from base.models.package import Package, PackageList

repos_commands_dir = "rep_commands"

class Packages(object):
	@controller.publish
	@controller.set_cache_expires(secs=0)
	def index(self, q=None):
		"""
		The is the main page which presents the list of packages
		if no key (q) is specified only the packages needing an action
		are shown.
		"""
		if not userinfo.is_admin():
			controller.http_redirect(controller.base_url()+'/login')
			
		class Stats():
			total = 0
			unclassified = 0
			unlinked = 0
		
		if q:
			db_packages = Package.query.filter_by(package=q).order_by(\
				asc(Package.package), asc(Package.version)).all()
		else:
			db_packages = Package.query.order_by( \
				asc(Package.package), asc(Package.version)).all()		
		packages = []
		last_package_version = None
		stats = Stats()
		
		# Walk the packages list, skip classified and linked
		for package in db_packages:
			package_version = package.package+"-"+package.version
			if package_version == last_package_version:
				continue
			if len(package.lists) == 0: # package is not in a repos
				continue
			last_package_version = package_version				
			stats.total += 1			
			app = None
			if package.install_class == None:
				stats.unclassified += 1				
			elif package.install_class == 'M':
				source_package = package.source or package.package
				app = Application.query.filter_by(
					source_package = source_package
				).first()
				if not app:
					stats.unlinked += 1
			if q or not package.install_class or \
				(package.install_class=='M' and not app):
					packages.append(package)
		return template.render("packages.html", packages = packages
			, stats = stats, q=q
		)
		
	@controller.publish		
	def set_class(self, package_id, install_class):
		""" Set the class_value for a package, select all packages
		which have a common name and version to the one identified
		by the package_id parameter """
		if not userinfo.is_admin():
			controller.http_error(403)			
		package = Package.query.filter_by(id = package_id).one()
		package_list = Package.query.filter_by(\
			package = package.package, version=package.version).all()
		for package in package_list:
			package.install_class = install_class
		return None

	@controller.publish		
	def search(self, q):
		""" Returns list of packages for the search box """
		if not userinfo.is_admin():
			controller.http_error(403)
			
		results = ""
		last_package = ""
		package_list = Package.query.filter(Package.package.like('%'+q+'%')).order_by(Package.package)
		for package in package_list:
			if package.package == last_package:
				continue
			last_package = package.package
			results += "%s|%d\n" % (package.package, package.id)
		return results
		
	@controller.publish		
	def remove(self, package_id, list_id, confirm=None):
		""" Create a command to remove a package from the repository """
		if not userinfo.is_admin():
			controller.http_error(403)	
		package_id	= long(package_id)
		list_id = long(list_id)
		package = Package.query.filter_by(id = package_id).first()
		packagelist = PackageList.query.filter_by(id = list_id).first()
		if not package:
			return "Package %d not found" % package_id
		if not packagelist:
			return "List %d not found" % list_id
		if confirm != "Y":
			return template.render("package_remove.html" \
				, package = package, packagelist = packagelist)
		source_package = package.source or package.package
		user = userinfo.find_user()
		action = "%s %s %s %s %s" % (user.email, 'remove' \
			, packagelist.suite, source_package, package.version)
			
		time_now = time.strftime("%Y%m%d.%H%M%S", time.localtime())
		filename = "%s_%s_%s" % (source_package, package.version, time_now)
		full_repos_cmd_dir  = os.path.join(apt_portal.base_dir, '..', repos_commands_dir)
		if not os.path.isdir(full_repos_cmd_dir):
			return "%s directory is not available, " \
				"repository commands are not supported" % \
				full_repos_cmd_dir
		os.umask(002)
		f = open(os.path.join(full_repos_cmd_dir, filename), 'w')
		os.umask(022)
		f.write(action)
		f.close()
		return template.render("package_remove.html" \
			, ticket_name = filename, confirm='Y')
			
	@controller.publish
	def copy(self, package_id, source_list_id, target_list):
		""" Create a command to copy a package to another repository """
		if not userinfo.is_admin():
			controller.http_error(403)
				
		package_id	= long(package_id)
		source_list_id = long(source_list_id)
		package = Package.query.filter_by(id = package_id).first()
		source_packagelist = PackageList.query.filter_by(id = source_list_id).first()
		target_packagelist = PackageList.query.filter_by(suite = target_list).first()
		if not package:
			return "Package %d not found" % package_id
		if not source_packagelist:
			return "List %d not found" % list_id
		if target_list and not target_packagelist:
			return "Repository %s not found" % target_list		
		repository_list = []
		for plist in PackageList.query.all():
			if plist.suite == source_packagelist.suite:
				continue
			if plist.suite not in repository_list:
				repository_list.append(plist.suite)
		if len(target_list) < 2:
			return template.render("package_copy.html" \
				, package = package \
				, source_packagelist = source_packagelist \
				, target_packagelist = target_packagelist \
				, repository_list = repository_list \
				, package_id = package_id \
				, source_list_id = source_list_id \
				, target_list = target_list \
				, asking = True \
				)
		source_package = package.source or package.package
		user = userinfo.find_user()
		action = "%s %s %s %s %s %s" % (user.email, 'copy' \
			, target_packagelist.suite, source_packagelist.suite, source_package, package.version)
			
		time_now = time.strftime("%Y%m%d.%H%M%S", time.localtime())
		filename = "%s_%s_%s" % (source_package, package.version, time_now)
		full_repos_cmd_dir  = os.path.join(apt_portal.base_dir, '..', repos_commands_dir)
		if not os.path.isdir(full_repos_cmd_dir):
			return "%s directory is not available, " \
				"repository commands are not supported" % \
				full_repos_cmd_dir
		os.umask(002)
		f = open(os.path.join(full_repos_cmd_dir, filename), 'w')
		os.umask(022)
		f.write(action)
		f.close()
		return template.render("package_copy.html" \
			, ticket_name = filename \
			, asking = False \
			)			

controller.attach(Packages(), "/packages")
