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
import os,gtk,gobject
import gst
import gst.interfaces

from lib_christine.gtk_misc import *
from lib_christine.gst_base import *

class discoverer(gtk.DrawingArea,christine_gconf):
	def __init__(self):
		christine_gconf.__init__(self)
		self.discoverer = gst.element_factory_make("playbin")
		self.discoverer.set_property("audio-sink",gst.element_factory_make("fakesink"))
		video_sink = gst.element_factory_make("fakesink")
		self.discoverer.set_property("video-sink",video_sink)
		self.discoverer.set_property("volume",0.0)
		self.bus = self.discoverer.get_bus()
		self.query_duration = self.discoverer.query_duration
		self.query_position = self.discoverer.query_position

	def watcher(self,bus,message):
		t = message.type
		if t == gst.MESSAGE_TAG:
			self.found_tags_cb(message.parse_tag())
		return True
	
	def set_location(self,file):
		self.tags = {}
		self.location = file
		self.discoverer.set_state(gst.STATE_NULL)
		self.discoverer.set_property("uri","file://%s"%self.location)
		#self.discoverer.set_state(gst.STATE_READY)
		self.discoverer.set_state(gst.STATE_PLAYING)
		self.discoverer.set_state(gst.STATE_PAUSED)
		return False
		
	def found_tags_cb(self,tags):
		if len(tags.keys()) > 0:
			for i in tags.keys():
				self.tags[i] = tags[i]
		
	def get_location(self):
		path = self.discoverer.get_property("uri")
		if path != None:
			path = path[7:]
		return path
	
	def get_tag(self,key):
		try:
			return self.tags[key]
		except:
			return ""
