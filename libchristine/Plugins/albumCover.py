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

from libchristine.Plugins.plugin_base import plugin_base
from libchristine.Plugins.lastfm import *
from libchristine.ui import interface
from libchristine.Share import Share
from libchristine.Tagger import Tagger
from libchristine.globalvars import IMAGEDIR
import urllib2
import thread
import os

class albumCover(plugin_base):
	def __init__(self):
		plugin_base.__init__(self)
		self.name = 'Album Cover'
		self.description = 'Try to get the album cover and shows on the gui if it is found.'
		self.iface = interface()
		self.tagger = Tagger()
		if not self.christineConf.exists('lastfm/getimage'):
			self.christineConf.setValue('lastfm/getimage', True)
		self.christineConf.notifyAdd('backend/last_played', self.getImage)
	
	def getImage(self, *args):
		if not self.active:
			return False
		if getattr(self, 'lastfmimage', False):
			self.lastfmimage.hide()
			self.lastfmimage.destroy()
		if not self.active:
			return
		file = self.christineConf.getString('backend/last_played')
		tags =  self.tagger.readTags(file)
		for key in ('artist','title', 'album'):
			if not tags[key]:
				pass
		thread.start_new(self.__getImage, (tags, ))
			
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
				name = os.path.split(image)[-1]
				f = urllib2.urlopen(image)
				name = os.path.split(image)[-1]
				g = open(os.path.join(IMAGEDIR, filename),"w")
				for line in f:
					g.write(line)
				g.close()
				have_image = True
		if have_image:
			self.lastfmimage = gtk.Image()
			pixbuf = self.gen_pixbuf_from_file(os.path.join(IMAGEDIR, filename))
			pixbuf = self.scalePixbuf(pixbuf, 150, 150)
			self.lastfmimage.set_from_pixbuf(pixbuf)
			self.interface.coreClass.VBoxList.pack_start(self.lastfmimage,
														False, False, 0)
			self.lastfmimage.show()
	
	def get_active(self):
		return self.christineConf.getBool('lastfm/getimage')
	
	def set_active(self, value):
		return self.christineConf.setValue('lastfm/getimage', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')