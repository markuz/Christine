#! /usr/bin/env python
# -*- coding: UTF-8 -*-

## Copyright (c) 2006 Marco Antonio Islas Cruz
## <markuz@islascruz.org>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


from libchristine.ChristineObject import ChristineObject

#from libchristine import Storage


class Dispatcher(ChristineObject):
	'''
	This class is able to import modules from packages and
	create instances of clases within a module.
	'''
	def __init__(self):
		'''
		Constructor. 
		'''
		pass
	
	def Import(self,package,name):
		'''
		Import a module from a given package
		@param pacakge string: Name of the package
		@param name (string): The name of the module to import
		'''
		if type(package) != str:
			raise TypeError("package argument must be a string")

		module = __import__(package,globals(),locals(),[name])
		return vars(module)[name]
