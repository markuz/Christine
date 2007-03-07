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


import pygst; pygst.require("0.10")
import os
import gtk
import gobject
import gst
import gst.interfaces

from lib_christine.GtkMisc import *
from lib_christine.gst_base import *

class Dscoverer(gtk.DrawingArea,ChristineGconf):
	def __init__(self):
		christine_gconf.__init__(self)
		self.__Discoverer = gst.element_factory_make("playbin")
		self.__Discoverer.set_property("audio-sink",gst.element_factory_make("fakesink"))
		self.__videoSink = gst.element_factory_make("fakesink")
		self.__Discoverer.set_property("video-sink",self.__videoSink)
		self.__Discoverer.set_property("volume",0.0)
		self.__Bus = self.__Discoverer.get_bus()
		self.query_duration = self.__Discoverer.query_duration
		self.query_position = self.__Discoverer.query_position

	def watcher(self,bus,message):
		t = message.type
		if t == gst.MESSAGE_TAG:
			self.found_tags_cb(message.parse_tag())
		return True
	
	def setLocation(self,file):
		'''
		receives a file in the first argument
		and puts it in the discoverer pipeline.
		'''
		self.tags = {}
		self.location = file
		self.__Discoverer.set_state(gst.STATE_NULL)
		self.__Discoverer.set_property("uri","file://%s"%self.location)
		#self.__Discoverer.set_state(gst.STATE_READY)
		self.__Discoverer.set_state(gst.STATE_PLAYING)
		self.__Discoverer.set_state(gst.STATE_PAUSED)
		return False
		
	def fountTagsCallBack(self,tags):
		if len(tags.keys()) > 0:
			for i in tags.keys():
				self.tags[i] = tags[i]
		
	def getLocation(self):
		'''
		returns the current location without the 'file://' part
		'''
		path = self.__Discoverer.get_property("uri")
		if path != None:
			path = path[7:]
		return path
	
	def getTag(self,key):
		try:
			return self.tags[key]
		except:
			return ""
