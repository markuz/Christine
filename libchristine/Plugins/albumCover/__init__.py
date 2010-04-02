#! /usr/bin/env python
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
# @category  Multimedia
# @package   Christine
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

#
# This module try to get the album cover and shows on the gui if it is found.
#

from libchristine.Plugins.plugin_base import plugin_base, christineConf
from libchristine.Plugins.lastfm import *
from libchristine.ui import interface
from libchristine.Share import Share
from libchristine.Tagger import Tagger
from libchristine.globalvars import IMAGEDIR
from libchristine.ChristineCore import ChristineCore

import gtk
import urllib2
import thread
import os

__name__ = _('Album Cover')
__description__  = _('Try to get the album cover and shows on the gui if it is found.')
__author__  = 'Marco Antonio Islas Cruz <markuz@islascruz.org>'
__enabled__ = christineConf.getBool('lastfm/getimage') 

class albumCover(plugin_base):
	def __init__(self):
		plugin_base.__init__(self)
		self.name = __name__
		self.description = __description__
		self.iface = interface()
		self.core = ChristineCore()
		self.tagger = Tagger()
		if not self.christineConf.exists('lastfm/getimage'):
			self.christineConf.setValue('lastfm/getimage', True)
		#self.christineConf.notifyAdd('backend/last_played', self.getImage)
		self.core.Player.connect('set-location', self.getImage)
	
	def getImage(self, *args):
		if getattr(self, 'lastfmimage', False):
			self.lastfmimage.hide()
			self.lastfmimage.destroy()
		if not self.active:
			return False
		if not self.set_image_from_directory():
			tags =  self.tagger.readTags(file)
			for key in ('artist','title', 'album'):
				if not tags[key]:
					pass
			thread.start_new(self.__getImage, (tags, ))
	
	def set_image_from_directory(self):
		'''
		Look for the album cover in the directory
		'''
		file = self.core.Player.getLocation()
		if not os.path.exists(file):
			return 
		directory = os.path.join(os.path.split(file)[:-1])
		if not directory:
			return
		directory = directory[0]
		files  = [k for k in os.listdir(directory) \
				if k.lower().startswith('cover') or \
				k.lower().startswith('folder') or\
				k.lower().startswith('albumart')]
		if files:
			self.set_image(os.path.join(directory, files[0]))
		return True
			
	def __getImage(self, tags):
		have_image = False
		filename = '_'.join((tags['artist'].replace(' ','_'),
							tags['album'].replace(' ','_')))
		filename += '.jpg'
		#TODO: Search for the cover in the file directory.
		if os.path.exists(os.path.join(IMAGEDIR, filename)):
			have_image = True
		else:
			sessionkey = self.christineConf.getString('lastfm/key')
			username = self.christineConf.getString('lastfm/name')
			user = User(username, APIKEY, SECRET, sessionkey)
			album = Album(tags['artist'], tags['album'], APIKEY, SECRET, sessionkey)
			image = album.getImage(IMAGE_LARGE)
			if image:
				f = urllib2.urlopen(image)
				name = os.path.split(image)[-1]
				g = open(os.path.join(IMAGEDIR, filename),"w")
				for line in f:
					g.write(line)
				g.close()
				have_image = True
		if have_image:
			self.set_image(os.path.join(IMAGEDIR, filename))
	
	def set_image(self, path):
		'''
		Set the image from the path
		'''
		try:
			if getattr(self, 'lastfmimage', False):
				self.lastfmimage.hide()
				self.lastfmimage.destroy()
			self.lastfmimage = gtk.Image()
			pixbuf = self.gen_pixbuf_from_file(path)
			pixbuf = self.scalePixbuf(pixbuf, 150, 150)
			self.lastfmimage.set_from_pixbuf(pixbuf)
			self.interface.coreClass.VBoxList.pack_start(self.lastfmimage,
														False, False, 0)
			self.lastfmimage.show()
		except:
			pass

	
	def get_active(self):
		return self.christineConf.getBool('lastfm/getimage')
	
	def set_active(self, value):
		__enabled__ = value 
		return self.christineConf.setValue('lastfm/getimage', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')
