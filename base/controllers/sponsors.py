# -*- coding: utf-8 -*-
from cherrypy_mako import *
from models.sponsor import *
from models.application import *
from sqlalchemy import desc

class Sponsors(object):
	@cherrypy.expose
	def index(self):
		maxval = 10
		sponsors = Sponsor.query.order_by(desc(Sponsor.ammount)).all()
		for sponsor in sponsors:
			if sponsor.ammount > maxval:
				maxval =  sponsor.ammount
		return serve_template("sponsors.html" \
			, sponsors = sponsors
			, maxval = maxval
			)

cherrypy.root.sponsors = Sponsors()
