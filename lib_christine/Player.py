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

class Player(gtk.DrawingArea,GtkMisc,christine_gconf,object):
	def __init__(self):
		self.__shouldShow = False
		christine_gconf.__init__(self)
		GtkMisc.__init__(self)
		gtk.DrawingArea.__init__(self)
		self.connect('destroy', lambda x:	self.__VideoSink.set_xwindow_id(0L))
		self.connect('expose-event', self.__ExposeCb)
		self.type = "sound"
		self.__CreatePlaybin()
		gobject.timeout_add(5000, self.__CheckScreensaver)
	
	def __CheckScreesaver(self):
		'''
		Check if we are whatching something with the player,
		if true, then deactivate the screensaver by resetting 
		the idle time.
		'''
		if self.__shouldShow: 
			a = os.popen("xscreensaver-command -deactivate 2&>/dev/null")
			b = os.popen("gnome-screensaver-command -d 2&> /dev/null")
		return True
		
	def __CreatePlaybin(self):
		'''
		Create the playbin
		'''
		self.__PlayBin	= gst.element_factory_make("playbin")
		self.__PlayBin.set_property("delay",GST_DELAY)
		self.play		= self.__PlayBin
		self.bus		= self.__PlayBin.get_bus()
		

		self.__UpdateAudioSink()
		self.__UpdateVideoSinksink()
		self.__UpdateAspectRatio()
		self.notify_add("/apps/christine/backend/audiosink",self.__UpdateAudioSink)
		self.notify_add("/apps/christine/backend/videosink",self.__UpdateVideoSinksink)
		self.notify_add("/apps/christine/backend/aspect-ratio",self.__UpdateAspectRatio)
		self.__UpdateAudioSink()
		self.__UpdateVideoSinksink()

		self.__visualizationPlugin = None

		self.__Connect()
		self.query_duration = self.__PlayBin.query_duration
		self.query_position = self.__PlayBin.query_position

	def __Connect(self):
		self.__PlayBin.set_property("audio-sink",self.__AudioSink_pack)
		self.__PlayBin.set_property("video-sink",self.__VideoSink)

	def __UpdateAudioSink(self,client="",cnx_id="",entry="",userdata=""):
		state = self.get_state()[1]
		self.__AudioSink_pack = gst.element_factory_make("bin")
		if self.get_location()!= None:
			self.pause()
		asink			= self.get_string("backend/audiosink")
		self.__AudioSink = gst.element_factory_make(asink)
		self.__AudioSink_pack.add(self.__AudioSink)

		self.audio_ghost = gst.GhostPad("sink",self.__AudioSink.get_pad("sink"))
		self.__AudioSink_pack.add_pad(self.audio_ghost)
		self.__PlayBin.set_property("audio-sink",self.__AudioSink_pack)

		if asink == "alsasink":
			self.__AudioSink.set_property("device","hw:0")
		if gst.State(gst.STATE_PLAYING) == state:
			self.playit()

	def __UpdateAudioSink(self,client="",cnx_id="",entry="",userdata=""):
		state = self.get_state()[1]
		if self.get_location()!= None:
			self.pause()
		vsink = self.get_string("backend/videosink") 
		self.__VideoSink = gst.element_factory_make(vsink)
		self.__PlayBin.set_property("video-sink",self.__VideoSink)
		if vsink in ["xvimagesink","ximagesink"]:
			self.__VideoSink.set_property("force-aspect-ratio",True)
		if gst.State(gst.STATE_PLAYING) == state:
			self.playit()
			self.__ExposeCb()


	def __UpdateAspectRatio(self,client="",cnx_id="",entry="",userdata=""):
		aspect_ratio	= self.get_string("backend/aspect-ratio")
		if aspect_ratio != None:
			self.__VideoSink.set_property("pixel-aspect-ratio",aspect_ratio)
	
	def __ExposeCb(self, window=None, event=None):
		'''
		Draw the player.
		'''
		# Drawing a black background because some 
		# GTK themes (clearlooks) don't draw it.
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


		self.__VideoSink.set_xwindow_id(self.window.xid)
		if self.__shouldShow:
			self.show()
			#print "display:",self.__VideoSink.get_property("display")

	def set_location(self,file):
		self.tags = {}
		self.__PlayBin.set_property("vis-plugin",self.__visualizationPlugin)
		if os.path.isfile(file):
			self.__PlayBin.set_state(gst.STATE_READY)
			nfile = "file://"+file
			self.__PlayBin.set_property("uri",nfile)
		else:
			print file.split(":")[0]
			if file.split(":")[0] in ["http","dvd","vcd"]:
				self.__PlayBin.set_property("uri",file)
			else:
				error("file %s not found"%os.path.split(file)[1])
		self.get_type()
		self.__ExposeCb()
			
	def playit(self):
		self.__PlayBin.set_state(gst.STATE_PLAYING)
	
	def pause(self):
		self.__PlayBin.set_state(gst.STATE_PAUSED)
		
	def stop(self):
		self.__PlayBin.set_state(gst.STATE_NULL)
		
	def seek_to(self,sec):
		nanos = sec * gst.SECOND
		self.__PlayBin.seek(nanos)
		
	def set_visualization_visible(self,active=False):
		#print "playbin.set_visualization_visible(",active,")"
		if self.get_location() != None:
			nanos = self.query_position(gst.FORMAT_TIME)[0]
		else:
			return True
		if active:
			vsink			= self.get_string("backend/vis-plugin") 
			self.__visualizationPlugin = gst.element_factory_make(vsink)
			self.__VideoSink.set_property("force-aspect-ratio",False)
			self.__shouldShow = True
		else:
			self.__visualizationPlugin = None
			self.__VideoSink.set_property("force-aspect-ratio",True)
			self.__shouldShow = False
			self.hide()
		self.__PlayBin.set_property("vis-plugin",self.__visualizationPlugin)
		self.__ExposeCb()
		state = self.__PlayBin.get_state()[1]
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
		self.__PlayBin.set_property("volume",volume)

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
		path = self.__PlayBin.get_property("uri")
		if path != None:
			if path.split(":")[0] == "file":
				path = path[7:]
			else:
				return path
		else:
			path = None
		return path

	def get_state(self):
		return self.__PlayBin.get_state()

	def get_type(self):
		if self.isvideo():
			self.type = "video"
		elif self.issound():
			self.type = "sound"
		else:
			pass

	def nano2str(self,nanos):
		'''
		returns something like 00:00:00.000000
		'''
		ts = nanos / gst.SECOND
		return '%02d:%02d:%02d.%06d' % (ts / 3600,
				ts / 60,ts % 60, nanos % gst.SECOND)

	def seek_to(self,sec):
		sec = long(sec)*gst.SECOND
		self.__PlayBin.seek(1.0,gst.FORMAT_TIME,gst.SEEK_FLAG_FLUSH,
				gst.SEEK_TYPE_SET,sec,gst.SEEK_TYPE_NONE,-1)

	def isvideo(self):
		if self.get_location() == None:
			return False
		ext = self.get_location().split(".").pop().lower()
		if "video-codec" in self.tags.keys() or \
			ext in video:
			self.__shouldShow = True
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
