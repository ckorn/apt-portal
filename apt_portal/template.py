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

	Template module
	Provides mako templating functions integrated with cherrypy.
	For more details on mako templates check:
		http://www.makotemplates.org/docs/
				
	The following additional functions are available_:
		_("text") - gettext translation support		_
	The following additional variables are available: 
		pagename - first path component of the url (http://site/lang/pagename/...)
		base_url - request base url ((http://base_url/pagename/...)
		self_url - request full url (without parameters)
		session - dictionary with current's sesion information		
		release	 - the current filter Ubuntu release number
"""

import time
import cgi
import cherrypy
import smtplib
import urllib
import apt_portal
from ConfigParser import NoOptionError, NoSectionError
from apt_portal import controller

from mako.lookup import TemplateLookup

_template_lookup = None



def set_directories(templates_directories, module_directory):
    """ 
	Sets the following configuration directories:
		templates_directories - list of dirs to lookup for templates
		module_directory - directory to keep cached template modules		
	"""	
    global _template_lookup, _media_base_url
    try:
        _media_base_url = apt_portal.get_config("media", "base_url") 
    except (NoOptionError, NoSectionError):
        _media_base_url = ''
    
    # Template rendering with internationalization support
    _template_lookup = TemplateLookup(directories=templates_directories 
    	, module_directory=module_directory 
    	, input_encoding='utf-8' 
    	, output_encoding='utf-8' 
    	, encoding_errors='replace' 
    	, default_filters=['strip_none'] 
    	, imports=['from apt_portal.template import strip_none, html_lines, quote']
	)

""" TODO: Translation using gettext """
def _(txt):
    return txt

def render(template_name, **kwargs):
    global _template_lookup, _media_base_url
    mytemplate = _template_lookup.get_template(template_name)
    
    # Global functions
    kwargs["_"] = _
    kwargs["session"] = controller.session 

    # Check if we need to use a lang prefix
    kwargs["pagename"] = pagename()
    kwargs["base_url"] = controller.base_url()
    kwargs["self_url"] = controller.self_url()
    kwargs["release"] = controller.selected_release
    kwargs["media_base_url"] = _media_base_url
    kwargs["current_release"] = controller.current_release
    kwargs["login_username"] = controller.session('login_username')    
    
    start_t = time.time()
    template_output = mytemplate.render(**kwargs)
    stop_t =  time.time()
    if not template_name.endswith('.mail'):
        template_output += '\n<!-- Template %s rendering took %0.3f ms -->\n' % \
            (template_name, (stop_t-start_t)*1000.0)
    return template_output

def get_template_def(templatename, defname):
    global _template_lookup
    mytemplate = _template_lookup.get_template(templatename)
    return mytemplate.get_def(defname).render()

"""
   The following are global variables extending the mako templates
"""
def pagename():
    """
    """
    page_parts = cherrypy.request.path_info.strip("/").split("/")
    if not page_parts:
        return None
    pagename = page_parts[0]
    #if pagename= "" and len(path_parts)>1:
    #    pagename = path_parts[len(path_parts) - 2]
    return pagename

def sendmail(template_filename, **kwargs):
    """
    Sends a mails using a mako template file
    @param template_filename: template to be used for the mail content
    @param kwargs: keyword arguments to be used on the template  
    """
    try:
        mail_server = apt_portal.get_config("mail", "smtp_server")
    except NoOptionError:
        mail_server = "localhost"

    message = render(template_filename, **kwargs)

    fromaddr = kwargs['sender']
    toaddrs = kwargs['destination']

    server = smtplib.SMTP(mail_server)
    server.sendmail(fromaddr, toaddrs, message)
    server.quit() 

# Because the unicode filter returns "None" for None strings
# We want to return '' for those
def strip_none(text):
    if text is None:
        return ''
    else:
        return unicode(text)

def html_lines(text):
    if text is None:
        return ''
    else:
        text = cgi.escape(unicode(text), True)		
        return text.replace('\n', '<br>')

def quote(text):
    return urllib.quote(text.decode('utf-8'))
