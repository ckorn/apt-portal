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


import cherrypy
import re
import apt_portal

# FIXME: selected_distro and current_release must be moved to a config file 
selected_distro = 'Ubuntu'
current_release  = '12.04'

selected_release = None
browser_distro = None
browser_release = None

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


def _precontroller():
    """ @summary
    The precontroller tool is used for the foollowing tasks:
    Based on the user agent string:
        Set cherrypy.request.user_distro_name  variable
        Set cherrypy.request.user_distro_version
    Based on the release cookie and cherrypy.request.user_distro_version
        Set selected_release
    """
    # static resources are not under precontroller control
    if cherrypy.request.config.get('tools.staticdir.on', False) or \
        cherrypy.request.config.get('tools.staticfile.on', False):
            return
        
    global selected_release, selected_distro, browser_distro, browser_release
    
    release = None
    
    user_agent = cherrypy.request.headers.get('User-Agent', None)    
    if user_agent:
        find_distro = re.findall('(Ubuntu)/([\d\.]*)', user_agent)
        if find_distro:
            browser_distro = find_distro[0][0]
            browser_release = find_distro[0][1]
            
    try:
        release = cherrypy.request.cookie["release"].value    
    except KeyError:
        pass
        
    if not release and browser_release:
        release = browser_release
    
    if release not in ['9.04', '9.10', '10.04', '10.10', '11.04', '11.10', '12.04', '12.10']:
        release = current_release
    
    selected_distro = 'Ubuntu'
    selected_release = release        
    
cherrypy.tools.precontroller = cherrypy.Tool('on_start_resource', _precontroller)

