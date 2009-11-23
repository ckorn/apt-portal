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
from apt_portal import controller, template
from base.models.sponsor import Sponsor
from sqlalchemy import desc

class Sponsors(object):
	@controller.publish
	def index(self):
		maxval = 10
		sponsors = Sponsor.query.order_by(desc(Sponsor.ammount)).all()
		for sponsor in sponsors:
			if sponsor.ammount > maxval:
				maxval =  sponsor.ammount
		return template.render("sponsors.html"
			, sponsors = sponsors
			, maxval = maxval
			)
controller.attach(Sponsors(), "/sponsors") 
