# -*- coding: utf-8 -*-
from apt_portal import controller, template
							
class Welcome(object):
	@controller.publish
	def index(self):
		return template.render("welcome.html")

controller.attach(Welcome(), "/welcome") 








