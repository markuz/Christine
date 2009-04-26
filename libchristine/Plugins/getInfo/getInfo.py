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
from libchristine.Translator import translate
from libchristine.Library import PATH
import gtk
import urllib2
import thread
import os

class getInfo(plugin_base):
	def __init__(self):
		'''
		Constructor
		'''
		plugin_base.__init__(self)
		self.name = 'getInfo'
		self.description = 'Shows/Update the info on the tags of the given file.'
		self.iface = interface()
		self.Share = Share()
		self.tagger = Tagger()
		self.iface.mainLibrary.connect('popping_menu', self.append_option)
	
	def append_option(self, library, menu):
		item =gtk.MenuItem(translate('Show info'))
		item.connect('activate', self.get_tags, library)
		menu.append(item)
	
	def get_tags(self, menu, library):
		#Obtain the current tags..
		model, iter = library.tv.get_selection().get_selected()
		if not iter:
			return False
		path = model.get_value(iter, PATH)
		tags = self.tagger.readTags(path)
		xml = self.Share.getTemplate('showInfo')
		pathlbl = xml['path']
		pathlbl.set_text(path)
		title = xml['title']
		title.set_text(tags['title'])
		artist = xml['artist']
		artist.set_text(tags['artist'])
		album = xml['album']
		album.set_text(tags['album'])
		genre = xml['genre']
		genre.set_text(str(tags['genre']))
		track_number = xml['track_number']
		track_number.set_text(str(tags['track']))
		dialog = xml ['dialog']
		response = dialog.run()
		dialog.destroy()
	
	def update_tags(self, path, key):
		'''
		Update the tags in the file
		'''
		self.iface.Player.set_tag(path, key)
		
		
	def get_active(self):
		return self.christineConf.getBool('lastfm/getinfo')
	
	def set_active(self, value):
		return self.christineConf.setValue('lastfm/getinfo', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')