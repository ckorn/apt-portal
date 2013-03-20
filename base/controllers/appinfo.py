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

    Application information editing
    
"""
import os
import imghdr
import Image

from sqlalchemy.exc import IntegrityError
from sqlalchemy import __version__ as sa_version

import apt_portal
from apt_portal import controller, template, database
from base.models.package import Package
from base.models.application import Application, ApplicationsCategory
from base.modules import userinfo


def app_by_id(id):
    """ Return app with id """
    app = Application.query.filter_by(id = id).first()
    return app
    
class AppInfo(object):
    @controller.publish
    @controller.set_cache_expires(secs=0)
    def edit(self, for_package_id = None, from_app_id = None):
        """ 
        Add/Edit an application record, after submission the browser
        will be redirected to the referer page
        """        
        if not userinfo.is_admin():
            controller.http_redirect(controller.base_url()+'/login/')
    
        # We need these to fill the combo box
        # do it here to avoid autoflush later
        categories = ApplicationsCategory.query.all()
        
        source_package = None
        application = None
        # the app info can be loaded from an app_id or for a package id
        if from_app_id:
            application = app_by_id(from_app_id)
            if not application:
                return "Application ID not found"
        elif for_package_id:
            package_id = for_package_id
            package = Package.query.filter_by(id = package_id).one()
            if not package:
                return "Package id %d not found" % package_id
            source_package = package.source or package.package
            
        if source_package: # we got a package hint
            application = Application.query.filter_by(\
                source_package = source_package).first()
    
        if not application: # app was not found, create new
            application = Application()
            application.source_package = source_package
    
        # Automatically set app name to source package
        # usefull hint on "for_package_id"                    
        if not application.name:
            application.name = source_package        
    
        # No changes here, save will be performed on edit_submit
        database.rollback()
        if sa_version.split(".") < ["0", "5", "0"]:
            database.clear()
        
        # Set the screenshot filename
        screenshot_filename = ""
        id = application.id
        if id:
            screenshot_filename = "/media/screens/%d/%d_t.png" % (id, id)            
        return template.render("app_edit.html" \
            , application = application \
            , categories = categories \
            , screenshot_filename = screenshot_filename \
        )
    
    @controller.publish
    def edit_submit(self, id, source_package, name, homepage, license, \
        descr, video_link, category):
        """ 
        Add/Edit an application record - submit
        """
        if not userinfo.is_admin():
            controller.http_redirect(controller.base_url()+'/login/')
                
        # Keep category query on top to avoid autoflush
        cat = ApplicationsCategory.query.filter_by(name=category).first()
        
        application = app_by_id(id) or Application()            
        application.source_package = source_package or None
        application.name = name
        application.homepage = homepage
        application.descr = descr.decode('utf-8')
        application.license = license
        application.video_link = video_link        
        if cat:
            application.category = cat
        else:
            return "ERROR: Could not find category", category                
        
        try:            
            database.commit()
        except IntegrityError as e:
            session.rollback()
            return "ERROR: Unable to update"
        
        id = application.id
        # db operation was succesful, update the screenshot if submited
        username = controller.session('login_username')
        filename = os.path.join(apt_portal.base_dir  , '../media/screens/%s_upload.png' % username)
        thumb_filename = os.path.join(apt_portal.base_dir, '../media/screens/%s_upload_t.png' % username)
        # There is a screenshot image to be uploaded
        if os.path.exists(filename):                
            screen_img_dir  = os.path.join(apt_portal.base_dir, "../media/screens/%d" % id)
            if not os.path.isdir(screen_img_dir):
                os.makedirs(screen_img_dir, 0755)                            
            dest = "%s/%s.png" % (screen_img_dir, id)
            thumb_dest = "%s/%d_t.png" % (screen_img_dir, id)
            os.rename(filename, dest)                
            os.chmod(dest, 0644)                    
            os.rename(thumb_filename, thumb_dest)
            os.chmod(thumb_dest, 0644)    
        return "OK "+str(application.id)
        
    @controller.publish
    def upload_screenshot(self, userfile):
        if not userinfo.is_admin():
            controller.http_error(403)
                    
        username = controller.session('login_username')
        data = userfile.file.read()
        filename = os.path.join(apt_portal.base_dir
            , '../media/screens/%s_upload.png' % username)
        thumb_filename = os.path.join(apt_portal.base_dir
            , '../media/screens/%s_upload_t.png' % username)
        return_thumb = '../media/screens/%s_upload_t.png' % username
        f = open(filename, 'wb')
        f.write(data)
        f.close()        
        img_type = imghdr.what(filename)
        if img_type != 'png':
            os.unlink(filename)
            return "ERROR: File format is not PNG!"
        # Create the thumbnail to present on the form
        # Calculate size to maintain aspect ratio
        size = 260, 205
        im = Image.open(filename)
        width = im.size[0]
        height = im.size[1]
        newwidth = int(size[0])
        newheight = int(height*(newwidth/float(width)))
        if newheight > int(size[1]):
            newheight = int(size[1])
            newwidth = int(width*(newheight/float(height)))
        size = newwidth, newheight
        # Resize and save the image
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(thumb_filename)
        return "/"+return_thumb
        
    @controller.publish
    def change_category(self, action, name):
        """ Add/Del a category """
        if not userinfo.is_admin():
            controller.http_error(403)        
        if action == "Add":
            appcat = ApplicationsCategory(name = name)
        else:
            appcat = ApplicationsCategory.query.filter_by(name = name).first()
            if appcat:
                appcat.delete();
        try:
            database.commit()
        except IntegrityError as e:
            pass
            
    @controller.publish
    def default(self, **args):
        print args

controller.attach(AppInfo(), "/appinfo")

