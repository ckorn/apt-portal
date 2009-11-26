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

    apt_portal package
    The following modules are provided:
        controller - controller setup
        database - database setup / low level interface
        template - template rendering
"""

import os
import sys
import signal
import time
import cherrypy
from cherrypy.process import plugins, servers
from cherrypy import _cplogging
from logging import handlers, DEBUG
from ConfigParser import ConfigParser


from apt_portal import template, database, controller

class Root(object):
    @cherrypy.expose
    def index(self):        
        controller.http_redirect('./welcome/')

class RootForce(object):
    def __init__(self, view):
        self.view = view

    @cherrypy.expose
    def index(self):
        return template.render(self.view)
      
    @cherrypy.expose
    def default(self, *args):
        raise controller.http_redirect('/')

"""
    Set cherrypy global configuration 
"""  
def set_default_config(application_name, options): 
    """ Set the cherrypy web server configuration """
    global app_name, base_dir, config
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
    
    
    config.read(os.path.join(base_dir, "..", 'applications' , app_name
                             , 'config', 'global.conf'))
    
    # Evalute all config items
    for section in config.sections():
        for key,value in config.items(section):            
            config.set(section, key, eval(value))
        
    # Set log rotation
    _set_rotated_logs()    
    _enable_base_static()

def _enable_base_static():
    global app_name, base_dir    
    base_static = ('js', 'css')
    conf = {}
    for dir in base_static:
        conf['/base/'+dir] = {\
                'tools.staticdir.on': True \
                ,'tools.staticdir.dir': os.path.join(base_dir \
                , '..', 'base', 'static', dir)
                }
    conf['/media'] =  {\
                'tools.staticdir.on': True \
                ,'tools.staticdir.dir': os.path.join(base_dir \
                , '..', 'media')
                }
    merge_config(conf)
    
        

def _set_rotated_logs(rot_maxBytes = 10000000, rot_backupCount = 1000):
    """
        Set the access logs to be rotated when they reach rot_maxBytes
        keeping a max of rot_backupCount log files
    """    
    global app, app_name, base_dir
    
    """ Set rotated logs for app """
    log = app.log
    
    # Create the application logs directory
    logs_dir = os.path.join(base_dir, '..', 'var', 'log', app_name)
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
    pid_dir = os.path.join(base_dir, '..', 'var', 'run')        
    pid_file = os.path.join(pid_dir, app_name+'.pid') 
    
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
    
def merge_config(conf):
    """ merge configuration into the current application config """
    global app
    app.merge(conf)
    
    
def get_config(*args):
    global config
    return config.get(*args)   

def is_running(app_name):
    """ Check if a given app is running based on it's pidfile """
    global base_dir
    pid_dir = os.path.join(base_dir, '..', 'var', 'run')        
    pid_file = os.path.join(pid_dir, app_name+'.pid') 
    # Check if there is a running pid
    try:
        f = open(pid_file, 'r')
    except IOError: # Unable to open
        return 0
    else:
        running_pid = int(f.readline())
        f.close()
    try:
        os.kill(running_pid, 0)
    except OSError:
        print "Application is not running, removing stale .pid file"
        os.unlink(pid_file)
        return 0
    else:
        return running_pid

def stop(app_name):
    """ Stop application using it's .pid file """
    retry = 0
    while retry < 3:    
        running_pid = is_running(app_name)
        if not running_pid:            
            if retry == 0: 
                print "Application was not running"
            break        
        print "Killing PID", running_pid     
        try:
            os.kill(running_pid, signal.SIGTERM)
        except OSError: # No such process
            print "Application was not running"
            break
        print "Waiting 5 seconds for the application termination"
        time.sleep(5)
        retry += 1

def set_app_static_dirs(directory_list):
    global app_name, base_dir
    conf = {'/':   {'tools.staticdir.root': os.path.join(base_dir \
            , '..', 'applications', app_name, 'static')}
        }
    
    # Setup the application related static content directories
    for dir in directory_list:
        conf['/'+dir] = {\
                'tools.staticdir.on': True \
                ,'tools.staticdir.dir': dir
                }    
    merge_config(conf)
    
    """ Add list of directories from the application dir as static contents """

    
    

app_name = None
config = ConfigParser()
base_dir = os.path.dirname(os.path.abspath(__file__))

cherrypy.root = Root()
app = cherrypy.tree.mount(cherrypy.root, '/')
