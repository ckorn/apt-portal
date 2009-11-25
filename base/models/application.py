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

from elixir import *
from sqlalchemy import UniqueConstraint

class Application(Entity):
	using_options(tablename='application')
	id = Field(Integer, primary_key=True)   
	name = Field(String(64), nullable = False, unique = True)
	homepage = Field(String(128), nullable = True)
	descr = Field(Unicode(512), nullable = False)
	license  = Field(String(64), nullable = False)
	note = Field(String(255), nullable = True)
	video_link 	= Field(String(128), nullable = True)
	source_package = Field(String(128), nullable = True, unique = True)
	category = ManyToOne('ApplicationsCategory', required = True)	
	using_table_options(mysql_engine='InnoDB')    
	
	def __repr__(self):
		return '<Application "%s", "%s">' % (self.name, self.descr)

class ApplicationsCategory(Entity):
	using_options(tablename='application_category')    
	name = Field(String(64), nullable = False, unique = True)	
	applications = OneToMany('Application')
	using_table_options(mysql_engine='InnoDB')

	def __repr__(self):
            return '<ApplicationsCategory "%s">' % self.name

setup_all(True)
