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
#  This file contains the database model for user information

from elixir import *
from sqlalchemy import UniqueConstraint

class Sponsor(Entity):
	using_options(tablename='sponsor')
	id = Field(Integer, primary_key = True)   
	name = Field(String(64), nullable = False)
	url = Field(String(128), nullable = False)
	ammount = Field(Integer, nullable = False)
	using_table_options(mysql_engine='InnoDB') 
		
	def __repr__(self):
		return '<Sponsor "%s">' % (self.name)

setup_all(True)
