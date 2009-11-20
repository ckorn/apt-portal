#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  (C) Copyright 2009, GetDeb Team - https://launchpad.net/~getdeb
#  --------------------------------------------------------------------
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  --------------------------------------------------------------------
#
#  This is just a wrapper file, the model is imported from the 
#  debfactory packages model

import sys
import os

packages_model_dir = 'debfactory/bin'

if not packages_model_dir in sys.path:
	sys.path.insert(0, packages_model_dir)
from packages_model import *
sys.path.remove(packages_model_dir)
