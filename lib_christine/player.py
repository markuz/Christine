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
import os,gtk,gobject, cairo
import gst
import gst.interfaces

from lib_christine.gtk_misc import *
from lib_christine.gst_base import *

BORDER_WIDTH=0

class player(gtk.DrawingArea,gtk_misc,christine_gconf,object):
	def __init__(self,main):
		self.main = main
		self.should_show = False
		christine_gconf.__init__(self)
		gtk_misc.__init__(self)
		gtk.DrawingArea.__init__(self)
		self.connect('destroy', lambda x:	self.video_sink.set_xwindow_id(0L))
		self.connect('expose-event', self.expose_cb)
		self.type = "sound"
		self.__create_playbin()
		gobject.timeout_add(5000, self.__check_screensaver)
	
	def __check_screensaver(self):
		if self.should_show: 
			a = os.popen("xscreensaver-command -deactivate")
			b = os.popen("gnome-screensaver-command -d 2&> /dev/null")
			#print a.read()
			#print b.read()
		return True
		
	def __create_playbin(self):
		self.playbin	= gst.element_factory_make("playbin")
		self.playbin.set_property("delay",GST_DELAY)
		self.play		= self.playbin
		self.bus		= self.playbin.get_bus()
		

		self.__update_audiosink()
		self.__update_videosink()
		self.__update_aspect_ratio()
		self.notify_add("/apps/christine/backend/audiosink",self.__update_audiosink)
		self.notify_add("/apps/christine/backend/videosink",self.__update_videosink)
		self.notify_add("/apps/christine/backend/aspect-ratio",self.__update_aspect_ratio)
		self.__update_audiosink()
		self.__update_videosink()

		self.vis_plugin = None

		self.__connect()
		self.query_duration = self.playbin.query_duration
		self.query_position = self.playbin.query_position

	def __connect(self):
		self.playbin.set_property("audio-sink",self.audio_sink_pack)
		self.playbin.set_property("video-sink",self.video_sink)

	def __update_audiosink(self,client="",cnx_id="",entry="",userdata=""):
		state = self.get_state()[1]
		self.audio_sink_pack = gst.element_factory_make("bin")
		if self.get_location()!= None:
			self.pause()
		asink			= self.get_string("backend/audiosink")
		self.audio_sink = gst.element_factory_make(asink)
		self.audio_sink_pack.add(self.audio_sink)

		self.audio_ghost = gst.GhostPad("sink",self.audio_sink.get_pad("sink"))
		self.audio_sink_pack.add_pad(self.audio_ghost)
		self.playbin.set_property("audio-sink",self.audio_sink_pack)

		if asink == "alsasink":
			self.audio_sink.set_property("device","hw:0")
		if gst.State(gst.STATE_PLAYING) == state:
			self.playit()

	def __update_videosink(self,client="",cnx_id="",entry="",userdata=""):
		state = self.get_state()[1]
		if self.get_location()!= None:
			self.pause()
		vsink = self.get_string("backend/videosink") 
		self.video_sink = gst.element_factory_make(vsink)
		self.playbin.set_property("video-sink",self.video_sink)
		if vsink in ["xvimagesink","ximagesink"]:
			self.video_sink.set_property("force-aspect-ratio",True)
		if gst.State(gst.STATE_PLAYING) == state:
			self.playit()
			self.expose_cb()


	def __update_aspect_ratio(self,client="",cnx_id="",entry="",userdata=""):
		aspect_ratio	= self.get_string("backend/aspect-ratio")
		if aspect_ratio != None:
			self.video_sink.set_property("pixel-aspect-ratio",aspect_ratio)


	def set_location(self,file):
		self.tags = {}
		self.playbin.set_property("vis-plugin",self.vis_plugin)
		if os.path.isfile(file):
			self.playbin.set_state(gst.STATE_READY)
			nfile = "file://"+file
			self.playbin.set_property("uri",nfile)
		else:
			print file.split(":")[0]
			if file.split(":")[0] in ["http","dvd","vcd"]:
				self.playbin.set_property("uri",file)
			else:
				error("file %s not found"%os.path.split(file)[1])
		self.get_type()
		self.expose_cb()
			
	def playit(self):
		self.playbin.set_state(gst.STATE_PLAYING)
	
	def pause(self):
		self.playbin.set_state(gst.STATE_PAUSED)
		
	def stop(self):
		self.playbin.set_state(gst.STATE_NULL)
		
	def seek_to(self,sec):
		nanos = sec * gst.SECOND
		self.playbin.seek(nanos)
		
	def set_visualization_visible(self,active=False):
			print "playbin.set_visualization_visible(",active,")"
			if self.get_location() != None:
				nanos = self.query_position(gst.FORMAT_TIME)[0]
			else:
				return True
			if active:
				vsink			= self.get_string("backend/vis-plugin") 
				self.vis_plugin = gst.element_factory_make(vsink)
				self.video_sink.set_property("force-aspect-ratio",False)
				self.should_show = True
			else:
				self.vis_plugin = None
				self.video_sink.set_property("force-aspect-ratio",True)
				self.should_show = False
				self.hide()
			self.playbin.set_property("vis-plugin",self.vis_plugin)
			self.expose_cb()
			state = self.playbin.get_state()[1]
			self.pause()
			self.set_location(self.get_location())
			self.seek_to(nanos/gst.SECOND)
			if gst.State(gst.STATE_PLAYING) == state:
				self.playit()
							
	def set_volume(self,volume):
		if volume < 0:
			volume = 0.0
		elif volume > 1:
			volume = 1.0
		self.playbin.set_property("volume",volume)

	def get_tag(self,key):
		try:
			return self.tags[key]
		except:
			return ""

	def found_tag_cb(self,tags):
		if len(tags.keys()) > 0:
			for i in tags.keys():
				self.tags[i] = tags[i]

	def get_location(self):
		path = self.playbin.get_property("uri")
		if path != None:
			if path.split(":")[0] == "file":
				path = path[7:]
			else:
				return path
		else:
			path = None
		return path
	def get_state(self):
		return self.playbin.get_state()

	def get_type(self):
		if self.isvideo():
			self.type = "video"
		elif self.issound():
			self.type = "sound"
		else:
			pass

	def nano2str(self,nanos):
		ts = nanos / gst.SECOND
		return '%02d:%02d:%02d.%06d' % (ts / 3600,
				ts / 60,ts % 60, nanos % gst.SECOND)

	def expose_cb(self, window=None, event=None):
		x,y,w,h = self.allocation
		self.context = self.window.cairo_create()
		self.context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		self.context.clip()
		self.context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		self.context.set_source_rgba(0,0,0)
		self.context.fill_preserve()
		self.context.set_source_rgb(0,0,0)
		self.context.stroke()


		self.video_sink.set_xwindow_id(self.window.xid)
		if self.should_show:
			self.show()
			#print "display:",self.video_sink.get_property("display")
			
	
	def seek_to(self,sec):
		sec = long(sec)*gst.SECOND
		self.playbin.seek(1.0,gst.FORMAT_TIME,gst.SEEK_FLAG_FLUSH,
				gst.SEEK_TYPE_SET,sec,gst.SEEK_TYPE_NONE,-1)

	def isvideo(self):
		if self.get_location() == None:
			return False
		ext = self.get_location().split(".").pop().lower()
		if "video-codec" in self.tags.keys() or \
			ext in video:
			self.should_show = True
			return True
		else:
			return False
		
	def issound(self):
		if self.get_location() == None:
			return False
		ext = self.get_location().split(".").pop().lower()
		if "audio-codec" in self.tags.keys() or \
				ext in sound:
			return True
		else:
			return False
