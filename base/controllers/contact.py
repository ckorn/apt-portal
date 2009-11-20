# -*- coding: utf-8 -*-
from cherrypy_mako import *
from mako.template import Template
from mako_mail import send_mail
from urlparse import urlparse

class Contact(object):
	@cherrypy.expose
	def index(self, name = None, email = None \
		, comment = None, submitting=None):		
		if not submitting:
			return serve_template("contact.html")

		# server side input validation
		if not name:
			return "Name is missing"
		if not email:
			return "Email is missing"
		if not comment or len(comment)<10:
			return "Comment is missing"

		referer_url = urlparse(cherrypy.request.headers['Referer'])
		referer_base = "%s://%s" % (referer_url.scheme, referer_url.netloc)		
		our_base = cherrypy.request.base
		if(referer_base != our_base):
			return "Not Allowed"
		destination = get_template_def(\
			"contact.html", "destination_email").strip()
		contact_mail = Template("""\
Return-Path: ${sender}
From: ${sender}
Subject: Contact Form
To: ${destination}

${comment}
""", input_encoding='utf-8', disable_unicode=True) # we alredy get unicode
		send_mail(mail_template = contact_mail\
			, sender = '"%s" <%s>' % (name, email) \
			, destination = destination \
			, comment = comment \
		)  
		return serve_template("contact.html", contact_received=1)

cherrypy.root.contact = Contact()
