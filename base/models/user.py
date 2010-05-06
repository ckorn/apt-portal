#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  (C) Copyright 2009, GetDeb Team - https://launchpad.net/~getdeb
#  --------------------------------------------------------------------
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  --------------------------------------------------------------------
#
#  This file contains the database model for user information

from elixir import *
from sqlalchemy import UniqueConstraint
from datetime import datetime

class User(Entity):
	using_options(tablename='user')
	id = Field(Integer, primary_key=True)    
	username = Field(String(64), nullable = False, unique = True)
	email = Field(String(64), nullable = False, unique = True)
	password = Field(String(42), nullable = False)
	authkey = Field(String(32), nullable = True)
	auth = Field(Integer(1), nullable = False)
	t_register = Field(DateTime, nullable = False)
	t_login = Field(DateTime, nullable = False)
	t_seen = Field(DateTime, nullable = False)
	lkey = Field(String(32), nullable = True)
	groups = ManyToMany('UsersGroup', ondelete='restrict', tablename="user_group_members")
	using_table_options(mysql_engine='InnoDB')    
	
	def __repr__(self):
		return '<User "%s %s">' % (self.username \
			, self.email)

class UsersGroup(Entity):
	using_options(tablename='user_group')    
	name = Field(String(64), nullable = False, unique = True)	
	users = ManyToMany('User', ondelete='restrict', tablename="user_group_members")
	using_table_options(mysql_engine='InnoDB')

	def __repr__(self):
            return '<UsersGroup "%s">' % self.name

setup_all(True)
