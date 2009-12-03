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
from optparse import OptionParser
from apt_portal import database

def add_admin(username):
        """ Add an username to the admin group """
        from base.models.user import User, UsersGroup
        admin_group = UsersGroup.query.filter_by(name = "Admin").first()
        if not admin_group: # if not found create it
            admin_group = UsersGroup(name = "Admin")
        user = User.query.filter_by(username = username).first()
        if not user:
            print "User %s is not registed" % username
            return 2
        if admin_group in user.groups:
            print "User %s is already on the admin group." \
                % username
            return 1
        else: # add it
            user.groups.append(admin_group)        
            user.auth = 1            
            database.commit()
            print "User %s added to the admin group." \
                % username
        return 0
    
def command_line_parser():
    """ 
    Returns an option parser object with the available 
    command line parameters
    """        
    parser = OptionParser()
    parser.add_option("-a", "--add-admin",
        action = "store", type="string", dest="add_admin",
        help = "Add an user to the admin group" \
        )                        
    parser.add_option("-b", "--bindip", \
        action = "store", type="string", dest="host", \
        help = "set bind address for the listener (default=127.0.0.1)" \
        , default="127.0.0.1")
    parser.add_option("-d", "--database",
        action = "store", type="string", dest="database",
        help = "specificy the database URI\n\n" \
        "Examples\n\n" \
        "   mysql://user:password@localhost/database" \
        "   sqlite:////database" \
        )        
    parser.add_option("-f", "--force-view", \
        action = "store", type="string", dest="force_view", \
        help = "force a specific view to be server for all requests\n" \
            "Usefull if you need to provide a maintenance warning")
    parser.add_option("-l", "--console-log", \
        action = "store_true", dest="console_log", default=False, \
        help = "print the http log to the console")
    parser.add_option("-n", "--no-fork", \
        action = "store_true", dest="no_fork", default=False, \
        help = "do not fork, run in the foreground")            
    parser.add_option("-p", "--port", \
        action = "store", type="string", dest="port", \
        help = "set bind address for the listener (default=8080)" \
            , default="8080" )                  
    parser.add_option("-s", "--sql-echo", \
        action = "store_true", dest="sql_echo", default=False, \
        help = "echo the sql statements")
    return parser