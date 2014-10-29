#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@copyright:
 
    (C) Copyright 2009-2010, APT-Portal Developers
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

@summary: 
    Distro informations functions
"""
def get_codename(distro, release):
    """ Return the codename for a given distro release """
    if release == 'all':
        release = '14.10'
    codemap = {}
    if distro.lower() == 'ubuntu':
        codemap = { '12.04' : 'precise',
                   '12.10' : 'quantal',
                   '13.04' : 'raring',
                   '13.10' : 'saucy',
                   '14.04' : 'trusty',
                   '14.10' : 'utopic'
                   }
    try:
        codename = codemap[release]
    except KeyError:
        codename = ''
    return codename

