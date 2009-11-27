#!/usr/bin/env python
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
"""
    Template module
    Provides database related functions (using python-elixir)
    For more information about elixir check http://elixir.ematia.de/trac/wiki
"""
import cherrypy
import elixir
from apt_portal import sqlalchemy_tool

def setup(db_url, sql_echo=False):
    """ Setup db url and sql echho """
    elixir.metadata.bind = db_url
    elixir.metadata.bind.echo = sql_echo
    
    # Setup SQLAlchemy transaction handler
    cherrypy.config.update({'tools.SATransaction.on' : True \
        , 'tools.SATransaction.dburi' : db_url \
        , 'tools.SATransaction.echo': sql_echo,
    })
    
def commit():
    """ Commit transactions for the current session """
    elixir.session.commit()

def rollback():
    """ Rollback any pending transactions for the currenet session """
    elixir.session.rollback()

def clear():
    elixir.session.clear()
        
def engine():
    return elixir.metadata.bind
