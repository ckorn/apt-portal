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

import hashlib
import string
from random import Random
import re
import cherrypy

from base.models.user import *


def md5pass(password, salt=None):    
    """ Returns the md5sum for a plain text password, using 10 chars salt """
    valid_salt_set = "0123456789"+string.letters
    salt_size = 10
    if salt:
        salt = salt[:salt_size]
    else:        
        salt = ''.join(Random().sample(valid_salt_set, salt_size))
    m = hashlib.md5()    
    m.update(salt+password)
    return salt+m.hexdigest()

def is_admin(user = None):
    """ Check if the user is member of the Admin group """
    if not user:
        if cherrypy.session.has_key('login_username'):
            user = User.query.filter_by(username = \
                cherrypy.session['login_username']).first()        
        else:
            return False
    if not user:
        return False
    admin_group = UsersGroup.query.filter_by(name = "Admin").first()
    if admin_group: 
        return (admin_group in user.groups)
    return False

def find_user(username = None):
    """  Return email from user"""    
    username = username or cherrypy.session.get('login_username', None)        
    user = User.query.filter_by(username = username).first()
    return user
    
    
def set_login_sesion_info(user):
    cherrypy.session['login_username'] = user.username
    cherrypy.session['is_admin'] = is_admin(user)

def generate_auth_key(length=32, chars=string.letters + string.digits):    
    return ''.join(Random().sample(chars, length))
    
def validateEmail(email):

    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

def validateUsername(username):

    if len(username) > 0:
        if re.match("^[a-zA-Z0-9\.]*$", username) != None:
            return True
    return False