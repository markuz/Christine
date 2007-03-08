# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2007 Marco Antonio Islas Cruz
#
# Christine is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Christine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @category  libchristine
# @package   Share
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import gtk.glade
from libchristine.Validator import *
from libchristine.pattern.Singleton import Singleton

#
# Share class manager for images, glade 
# templates and more files
#
# @author Miguel Vazquez Gocobachi <demrit@gnu.org>
# @since 0.3
class Share(Singleton):
	"""
	Share class manager for images, glade 
	templates and more files
	"""
	#
	# Directory where we have template files
	#
	# @var string
	__PathTemplate = None
	
	#
	# Directory where we have images
	#
	# @var string
	__PathPixmap = None
	
	#
	# Constructor
	#
	# @param  string sharePath Path to share files
	# @return void
	def __init__(self, sharePath = '/usr/local/share/christine'):
		"""
		Constructor
		"""
		self.setName('Share')
		self.__PathTemplate = sharePath + '/gui/'
		self.__PathPixmap   = sharePath + '/gui/pixmap/'
	
	#
	# Gets glade template
	#
	# @param  string file The file name without extension
	# @return string or None
	def getTemplate(self, file = None):
		"""
		Gets glade template
		"""
		if ((not isNull(file)) or (isStringEmpty(file)):
			file + '.glade'
			if (isFile(self.__PathTemplate + file)):
				return gtk.glade.XML(self.__PathTemplate + file, None, None)

		return None
	
	#
	# Gets image as path string
	#
	# @param  string name The image name without extension
	# @return string or None
	def getImage(self, name):
		"""
		Gets image as path string
		"""
		if ((not isNull(file)) or (isStringEmpty(file)):
			if (isFile(self.__PathPixmap + file + '.png')):
				return self.__PathTemplate + file + '.png'
			elif (isFile(self.__PathPixmap + file + '.svg')):
				return self.__PathTemplate + file + '.svg'

		return None
