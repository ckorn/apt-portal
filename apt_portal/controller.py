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

def attach(controller, controller_path_name):    
    controller_path_name = controller_path_name.strip("/")
    setattr(cherrypy.root, controller_path_name, controller)
   
def attach_error_handler(http_error_code, func): 
 cherrypy.config.update({'error_page.%s' % http_error_code : func})
 
def publish(func=None, *args):   
    return cherrypy.expose(func, *args)

def set_cache_expires(secs=0, force=False):    
    return cherrypy.tools.expires(secs=secs, force=force)

def http_redirect(url):
    raise cherrypy.HTTPRedirect(url)

def http_error(http_error_code):
    raise cherrypy.HTTPError(403)

def base_url():
    """ Return the site base url, TODO: hostname+language""" 
    return cherrypy.request.base

def self_url():
    """
    @return: the current request url
    """
    return cherrypy.request.path_info

def get_header(header, default_value=None):
    """
    @param header: header field name
    @default_value: value to be returned if header is not found
    @return: request header value
    """
    return cherrypy.request.headers.get(header, default_value)

def session(item, default=None):
    return cherrypy.session.get(item, default)

def delete_session():
    """
    Delete the current request session 
    """
    cherrypy.session.delete()
    cherrypy.lib.sessions.expire()
        
from apt_portal import pre_controller_tool
