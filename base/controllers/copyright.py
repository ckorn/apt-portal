# -*- coding: utf-8 -*-
from cherrypy_mako import *

class Copyright(object):
    @cherrypy.expose
    def index(self):
        return serve_template("copyright.html")

cherrypy.root.copyright = Copyright()
