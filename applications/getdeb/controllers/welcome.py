# -*- coding: utf-8 -*-
from apt_portal import controller, template
from base.modules import sponsors

class Welcome(object):
	@controller.publish
	def index(self):
		(sponsor, sponsor_total) = sponsors.get_sponsor()
		return template.render("welcome.html", sponsor = sponsor
							   , sponsor_total = sponsor_total)

controller.attach(Welcome(), "/welcome") 
