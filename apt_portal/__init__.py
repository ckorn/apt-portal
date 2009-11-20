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
    apt_portal package
    The following modules are provided:
        controller - controller setup
        database - database setup / low level interface
        template - template rendering
"""
import os
import sys
import cherrypy
from cherrypy import _cplogging
from logging import handlers, DEBUG


from apt_portal import template, database, controller

"""
    Set cherrypy global configuration 
"""  
def set_default_config(application_name, options): 
    """ Set the cherrypy web server configuration """
    global app_name, base_dir
    app_name = application_name    

    aptportal_threads = int(os.environ.get('APTPORTAL_THREADS', 100))
    
    # Set network related options and optional console log
    cherrypy.config.update({'environment': 'production',
                            'server.socket_host': options.host,
                            'server.socket_port': int(options.port),
                            'server.thread_pool': aptportal_threads,
                            'log.screen': options.console_log})
                            
    # Enable gzip compression
    cherrypy.config.update({'tools.gzip.on': 'True'})
        
    # Enable sessions support
    if not os.path.isdir('/tmp/cherrypy_sessions_' + app_name):
        os.mkdir('/tmp/cherrypy_sessions_' + app_name, 0700)    
        
    cherrypy.config.update({'tools.sessions.on': True \
        , 'tools.sessions.storage_type': "file" \
        , 'tools.sessions.storage_path': "/tmp/cherrypy_sessions_"  + app_name \
        , 'tools.sessions.timeout': 60 \
        
    })

    # Enforce utf8 encoding
    cherrypy.config.update({'tools.encode.on':True \
        , 'tools.encode.encoding':'utf-8' \
        , 'tools.encode.errors':'replace' \
    })
        
    # Enable the precontroller tool
    cherrypy.config.update({'tools.precontroller.on': 'True'})
    
    # Set log rotation
    _logs_rotation(app, app_name)    
    _enable_base_static()
    _enable_app_static()

def _enable_base_static():
    global app_name, base_dir    
    base_static = ('js', 'css')
    conf = {}
    for dir in base_static:
        conf['/base/'+dir] = {\
                'tools.staticdir.on': True \
                ,'tools.staticdir.dir': os.path.join(base_dir \
                , 'base', 'static',dir)}
    merge_config(conf)
    
def _enable_app_static():
    """ """
    global app_name, base_dir
    _enable_base_static()
    
    # Setup the application related static content directories    
    conf = {'/':   {'tools.staticdir.root': os.path.join(base_dir \
                , '..', 'applications', app_name, 'static')}
            }
    
    
    cherrypy.config.update(os.path.join(base_dir, "..", 'applications' \
        , app_name, 'config', 'base.conf'))
    
    merge_config(conf)

def _logs_rotation(rot_maxBytes = 10000000, rot_backupCount = 1000):
    global app, app_name, base_dir
    
    """ Set rotated logs for app """
    log = app.log
    
    # Create the application logs directory
    logs_dir = os.path.join(base_dir, 'logs', app_name)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, 0700)

    # Remove the default FileHandlers if present.
    log.error_file = ""
    log.access_file = ""

    maxBytes = getattr(log, "rot_maxBytes", rot_maxBytes)    
    backupCount = getattr(log, "rot_backupCount", rot_backupCount)

    # Make a new RotatingFileHandler for the error log.
    fname = getattr(log, "rot_error_file", "%s/error.log" % logs_dir)
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(DEBUG)
    h.setFormatter(_cplogging.logfmt)
    log.error_log.addHandler(h)

    # Make a new RotatingFileHandler for the access log.
    fname = getattr(log, "rot_access_file", "%s/access.log" % logs_dir)
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(DEBUG)
    h.setFormatter(_cplogging.logfmt)
    log.access_log.addHandler(h)

def start(run_on_foreground):    
    engine = cherrypy.engine
    if not run_on_foreground:        
        print "Running in background"
        if not os.path.exists(pid_dir):
            os.makedirs(pid_dir, 0755)
        plugins.PIDFile(engine, pid_file).subscribe()    
        plugins.Daemonizer(engine).subscribe()     
    """Setup the signal handler to stop the application while running"""
    if hasattr(engine, "signal_handler"):
        engine.signal_handler.subscribe()
    if hasattr(engine, "console_control_handler"):
        engine.console_control_handler.subscribe()
                   
    try:
        engine.start()
    except:
        print "ERROR: Unable to start engine, check the error log"
        sys.exit(1)
    else:        
        engine.block()

def merge_config(conf):
    """ merge configuration into the current application config """
    global app
    app.merge(conf)    

class Root(object):
    @cherrypy.expose
    def index(self):        
        raise cherrypy.HTTPRedirect('./welcome/')

class RootForce(object):
    def __init__(self, view):
        self.view = view

    @cherrypy.expose
    def index(self):
        return serve_template(self.view)
      
    @cherrypy.expose
    def default(self, *args):
       raise cherrypy.HTTPRedirect('/')


app_name = None
base_dir = os.path.dirname(os.path.abspath(__file__))
print "bd:", base_dir
cherrypy.root = Root()
app = cherrypy.tree.mount(cherrypy.root, '/')
