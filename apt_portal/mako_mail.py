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
import smtplib
from cherrypy_mako import *

def send_mail(template_name=None, mail_template=None, **kwargs):
	"""
	Sends a mails using a mako template file
	"""
	if template_name:
		message = serve_template(template_name, **kwargs)
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
