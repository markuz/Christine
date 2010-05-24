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
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2007-2009 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
#import gtk.glade
# @author Miguel Vazquez Gocobachi <demrit@gnu.org>

from libchristine.Validator import *
from libchristine.pattern.Singleton import Singleton
from libchristine.gui.GtkMisc import glade_xml
from libchristine.globalvars import DATADIR, SHARE_PATH
from libchristine.Logger import LoggerManager
from libchristine.options import options
import time
import os
import gtk
import sys
import gobject


#
# Share class manager for images, glade
# templates and more files
#
# @author Miguel Vazquez Gocobachi <demrit@gnu.org>
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

	def __init__(self):
		"""
		Constructor
		"""
		self.setName('Share')
		self.__logger = LoggerManager().getLogger('Share')
		self.__PathTemplate = os.path.join(SHARE_PATH, 'gui')
		self.__PathPixmap   = os.path.join(self.__PathTemplate, 'pixmaps')
		#self.__Pixmaps, used to store a pixmap. if it is here then reuse it
		#instead of creating another one from the same faile
		self.__Pixmaps = {}
		gobject.timeout_add(1000, self.check_pixmap_time_access)

	def getTemplate(self, file, root = None):
		"""
		Gets glade template
		@param string file: file to load
		@param string root: root widget to return instead the main window
		"""
		if file:
			file = ''.join([file, '.glade'])
			if isFile(os.path.join(self.__PathTemplate, file)):
				return glade_xml(os.path.join(self.__PathTemplate, file),root)
		self.__logger.warning('File %s was not found'%(os.path.join(self.__PathTemplate, file)))
		return None
	
	def getImage(self, name):
		"""
		Gets image as path string
		"""
		if ((not isNull(file)) or (isStringEmpty(name))):
			if (isFile(os.path.join(self.__PathPixmap, name+'.png'))):
				return os.path.join(self.__PathPixmap, name+'.png')
			elif (isFile(os.path.join(self.__PathPixmap, name+ '.svg'))):
				return os.path.join(self.__PathPixmap, name+'.svg')
		return None

	def getImageFromPix(self, name):
		"""
		Gets image from pixbuf
		"""
		icon_theme = gtk.icon_theme_get_default()
		if icon_theme.has_icon(name):
			pixbuf = icon_theme.load_icon(name, 48, 0)
			return pixbuf
		else:
			return self.load_from_local_dir(name)

	def load_from_local_dir(self, name):
		if not name: return 
		files = os.listdir(self.__PathPixmap)
		filesf = [k for k in files if len(k.split('.')) > 1 \
				and k.split('.')[0].startswith(name)]
		if not filesf:
			self.__logger.warning('None of this files \n%s\n where found'%repr(name))
			return
		filepath = os.path.join(self.__PathPixmap, filesf[0])
		pixdir = self.__Pixmaps.get(filepath,{})
		if not pixdir:
			self.__Pixmaps[filepath] = pixdir
			pixmap = gtk.gdk.pixbuf_new_from_file(filepath)
			self.__Pixmaps[filepath]['pixmap'] = pixmap
		self.__Pixmaps[filepath]['timestamp'] = time.time()
		return self.__Pixmaps[filepath]['pixmap']

	
	def check_pixmap_time_access(self):
		'''
		Check the last time access to a pixmap, if the diference between
		the current time and the last access time is more than 600 senconds 
		(10 minutes) then it will erase the pixmap.
		'''
		c ={}
		ctime = time.time()
		for key, value in self.__Pixmaps.iteritems():
			if ctime - value['timestamp'] < 60:
				c[key] = value
		self.__Pixmaps = c.copy()
		#del c
		return True
