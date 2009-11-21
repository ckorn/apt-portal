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


import re
import cgi
import cherrypy
import smtplib
import apt_portal

from urlparse import urlparse
from mako.template import Template
from mako.lookup import TemplateLookup

template_lookup = None

def set_directories(templates_directories, module_directory):
	""" 
	Sets the following configuration directories:
		templates_directories - list of dirs to lookup for templates
		module_directory - directory to keep cached template modules		
	"""	
	global template_lookup
		
	# Template rendering with internationalization support
	template_lookup = TemplateLookup(directories=templates_directories 
		, module_directory=module_directory 
		, input_encoding='utf-8' 
		, output_encoding='utf-8' 
		, encoding_errors='replace' 
		, default_filters=['strip_none'] 
		, imports=['from apt_portal.template import strip_none, html_line_breaks']
	)

""" TODO: Translation using gettext """
def _(txt):
	return txt
	
def render(templatename, **kwargs):
	global template_lookup
	mytemplate = template_lookup.get_template(templatename)

	# Global functions
	kwargs["_"] = _
	kwargs["session"] = session 
		
	# Check if we need to use a lang prefix
	kwargs["pagename"] = pagename()
	kwargs["base_url"] = apt_portal.base_url()
	kwargs["self_url"] = cherrypy.request.path_info
	kwargs["release"] = cherrypy.request.release
	kwargs["login_username"] = None
	if cherrypy.session.has_key('login_username'):
		kwargs["login_username"] = cherrypy.session['login_username']
	return mytemplate.render(**kwargs)

def get_template_def(templatename, defname):
	global mylookup
	mytemplate = mylookup.get_template(templatename)
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


"""
   The following are global functions  extending the mako templates
"""	
def session(key):
	""" Return value for a given session key, None if not found """
	if not cherrypy.session:
		return None
	return cherrypy.session.get(key, None)

def sendmail(template_name=None, mail_template=None, **kwargs):
	"""
	Sends a mails using a mako template file
	"""
	if template_name:
		message = render(template_name, **kwargs)
	elif mail_template:
		message = mail_template.render(**kwargs)
	else:
		raise
	fromaddr = kwargs['sender']
	toaddrs = kwargs['destination']
	try:
		server = smtplib.SMTP('localhost')
		server.sendmail(fromaddr, toaddrs, message)
		server.quit() 
	except Exception:
		print "There was an error sending mail"
		pass

# Because the unicode filter returns "None" for None strings
# We want to return '' for those
def strip_none(text):
	if text is None:
		return ''
	else:
		return unicode(text)

def html_line_breaks(text):
	if text is None:
		return ''
	else:
		text = cgi.escape(unicode(text), True)		
		return text.replace('\n', '<br>')
