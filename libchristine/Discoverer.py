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
# @package   Discoverer
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import pygst; pygst.require('0.10')
import os
import gtk
import gobject
import gst
import gst.interfaces

from libchristine.GtkMisc import *
from libchristine.GstBase import *
from libchristine.Validator import *
from libchristine.Preferences import Preferences

class Discoverer(gtk.DrawingArea,Preferences):
	def __init__(self):
		"""
		Constructor
		"""
		Preferences.__init__(self)
		self.__Discoverer = gst.element_factory_make('playbin')
		self.__VideoSink  = gst.element_factory_make('fakesink')

		self.__Discoverer.set_property('audio-sink', gst.element_factory_make('fakesink'))
		self.__Discoverer.set_property('video-sink', self.__VideoSink)
		self.__Discoverer.set_property('volume',     0.0)
		
		# self.Bus must be public
		self.Bus            = self.__Discoverer.get_bus()
		self.query_duration = self.__Discoverer.query_duration
		self.query_position = self.__Discoverer.query_position

	#
	# Watcher for Player
	#
	# @param
	# @param
	# @return boolean
	def watcher(self, bus, message):
		"""
		Watcher for player
		"""
		if (message.type == gst.MESSAGE_TAG):
			self.callbackFoundTags(message.parse_tag())

		return True
	
	#
	# Receives a file in the first argument
	# and puts it in the discoverer pipeline
	#
	# @return boolean
	def setLocation(self, file):
		"""
		Receives a file in the first argument
		and puts it in the discoverer pipeline
		"""
		self.__Tags     = {}
		self.__Location = file

		self.__Discoverer.set_property('uri', "file://%s" % self.__Location)

		self.__Discoverer.set_state(gst.STATE_NULL)
		self.__Discoverer.set_state(gst.STATE_READY)
		self.__Discoverer.set_state(gst.STATE_PLAYING)
		self.__Discoverer.set_state(gst.STATE_PAUSED)

		return False
		
	#
	# Callback foundTags
	#
	# @return void
	def callbackFoundTags(self, tags):
		"""
		Callback found tags
		"""
		if (len(tags.keys()) > 0):
			for i in tags.keys():
				self.__Tags[i] = tags[i]
	
	#
	# Returns path location for a file
	#
	# @return string
	def getLocation(self):
		"""
		returns the current location without the 'file://' part
		"""
		path = self.__Discoverer.get_property('uri')
		
		if (not isNull(path)):
			path = path[7:]

		return path
	
	#
	# Gets tag with a key
	#
	# @return string
	def getTag(self, key):
		"""
		Gets tag with a key
		"""
		try:
			return self.__Tags[key]
		except:
			return ''
