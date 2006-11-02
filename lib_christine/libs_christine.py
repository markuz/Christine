#! /usr/bin/env python
# -*- coding: UTF8 -*-

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
import cPickle as pickle
import gst
import gst.interfaces

from lib_christine.gtk_misc import *




GST_DELAY = 0
wdir = os.environ["HOME"]+"/.christine/"
CHRISTINE_AUDIO_EXT = sound = ["mp3","ogg","wma"]
CHRISTINE_VIDEO_EXT = video = ["mpg","mpeg","mpe","avi"]

class sanity:
	'''
		Make all the sanity checks
	'''
	def __init__(self):
		self.__check_christine_dir()

	def __check_christine_dir(self):
		if not os.path.exists(wdir):
			os.mkdir(wdir)
		else:
			if os.path.isfile(wdir):
				os.unlink(wdir)
				self.__check_christine_dir()


class lib_library:
	def __init__(self,list):
		sanity()
		if os.path.exists(os.path.join(wdir,list)):
			f =	open(os.path.join(wdir,list),"r")
			self.files = pickle.load(f)
			f.close()
		else:
			self.files = {}
		self.list = list

	def __setitem__(self,name,path):
		self.append(name,path)

	def __getitem__(self,key):
		return self.files[key]
		
	def append(self,name,data):
		if type(data) != type({}):
			raise TypeError, "data must be a dict, got %s"%type(data)
		self.files[name]=data

	def keys(self):
		return self.files.keys()
	
	def save(self):
		f = open(wdir+self.list,"w")
		pickle.dump(self.files,f)
		f.close()

	def clear(self):
		self.files.clear()
	
	def remove(self,key):
		c = {}
		if key in self.keys():
			for i in self.keys():
				if i != key:
					c[i]= self.files[i]
			self.files = c.copy()
			#print "%s removed"%key
		else:
			#print "key %s not found"%key
			pass
	
	def get_type(self,file):
		ext = file.split(".").pop()
		if ext in sound:
			return "sound"
		if ext in video:
			return "video"
	
	def get_sounds(self):
		a = {}
		for i in self.keys():
			if self.files[i]["type"] == "audio":
				a[i] = self.files[i]
		return a

	def get_videos(self):
		a = {}
		for i in self.keys():
			if self.files[i]["type"] == "video":
				a[i] = self.files[i]
		return a

		
class play10(gtk.DrawingArea,gtk_misc,christine_gconf):
	def __init__(self,main):
		self.main = main
		self.should_show = False
		christine_gconf.__init__(self)
		gtk_misc.__init__(self)
		gtk.DrawingArea.__init__(self)
		self.connect('destroy', self.destroy_cb)
		self.connect('expose-event', self.expose_cb)
		self.type = "sound"
		self.__create_playbin()
		#self.__create_fakeplay()
	
		
	def __create_playbin(self):
		self.playbin	= gst.element_factory_make("playbin")
		#self.playbin.set_state(gst.STATE_READY)
		self.playbin.set_property("delay",GST_DELAY)
		self.play		= self.playbin
		self.bus		= self.playbin.get_bus()
		

		#self.bus.add_watch(self.error_handler)
		#self.playbin.connect("error",self.error_handler)
		asink			= self.get_string("backend/audiosink")
		self.audio_sink = gst.element_factory_make(asink)
		#print "asink",asink
		if asink == "alsasink":
			self.audio_sink.set_property("device","hw:0")
		vsink			= self.get_string("backend/videosink") 
		aspect_ratio	= self.get_string("backend/aspect-ratio")

		self.video_sink = gst.element_factory_make(vsink)
		if vsink == "xvimagesink" or vsink == "ximagesink":
			self.video_sink.set_property("force-aspect-ratio",True)

		if aspect_ratio != None:
			self.video_sink.set_property("pixel-aspect-ratio",aspect_ratio)
		vsink			= self.get_string("backend/vis-plugin") 
		self.vis_plugin = gst.element_factory_make(vsink)

		self.__connect()
		self.query_duration = self.playbin.query_duration
		self.query_position = self.playbin.query_position

	def __connect(self):
		self.playbin.set_property("video-sink",self.video_sink)
		self.playbin.set_property("audio-sink",self.audio_sink)
		self.playbin.set_property("vis-plugin",self.vis_plugin)

	# player10 Set location
	def set_location(self,file):
		#print "self.tags={}"
		self.tags = {}
		if os.path.isfile(file):
			self.playbin.set_state(gst.STATE_READY)
			nfile = "file://"+file
			#print "nfile:",nfile
			#print "self.playbin.set_property(\"uri\",nfile)"
			self.playbin.set_property("uri",nfile)
			#self.discoverer = gst.extend.discoverer.Discoverer(file)
			#gobject.timeout_add(500,self.print_discover)
			#print "self.pause()"
			#self.pause()
			#print "set_location is done"
		else:
			#print file
			if file.split(":")[0] == "http":
				self.playbin.set_property("uri",file)
			else:
				error("file %s not found"%os.path.split(file)[1])
		#print "set_location check:",self.playbin.get_property("uri")
		self.get_type()
		self.expose_cb()
			
	def print_discover(self,widget=None,b=None):
		#print widget,b
		self.discoverer.discover()
		#print self.discoverer.print_info()
		#print "tags:",self.discoverer.tags
		self.tags = self.discoverer.tags
		if len(self.discoverer.tags.keys()):
			return False
		return True

	def playit(self):
		self.playbin.set_state(gst.STATE_PLAYING)
		#gobject.timeout_add(1000,self.check)
	
	def check(self):
		#print self.playbin.get_property("queue-size")
		return True
		
	def pause(self):
		self.playbin.set_state(gst.STATE_PAUSED)
		#self.audio_sink.set_state(gst.STATE_PAUSED)
		#self.video_sink.set_state(gst.STATE_PAUSED)
		
	def stop(self):
		self.playbin.set_state(gst.STATE_NULL)
		
	def seek_to(self,sec):
		nanos = sec * gst.SECOND
		self.playbin.seek(nanos)
		
	def set_visualization_visible(self,active=False):
		print "playbin.set_visualization_visible(",active,")"
		if active:
			self.playbin.set_property("vis-plugin",self.vis_plugin)
			# The try/except is to avoid a QueryError when
			# there is no uri in the player.
			try:
				nanos = self.query_position(gst.FORMAT_TIME)[0]
			except gst.QueryError:
				nanos = 0
			self.should_show = True
			self.expose_cb()
			self.playbin.seek(1.0,gst.FORMAT_TIME,gst.SEEK_FLAG_FLUSH,
				gst.SEEK_TYPE_SET,nanos,gst.SEEK_TYPE_NONE,-1)
			if self.playbin.get_state() == gst.STATE_PLAYING:
				sefl.pause()
				self.playit()

		else:
			self.playbin.set_property("vis-plugin",None)
			if self.type == "sound":
				self.hide()
				
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
		#print __name__,"fount_tags_cb",self.tags

	def get_location(self):
		path = self.playbin.get_property("uri")
		if path != None:
			if path.split(":")[0] == "file":
				path = path[7:]
			else:
				return path
		else:
			path = None
		#print "player.get_location:",path
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
			#raise TypeError,"Not an known video or sound"

	def nano2str(self,nanos):
		ts = nanos / gst.SECOND
		return '%02d:%02d:%02d.%06d' % (ts / 3600,
				ts / 60,ts % 60, nanos % gst.SECOND)

	def destroy_cb(self, da):
		self.video_sink.set_xwindow_id(0L)
		
	def expose_cb(self, window=None, event=None):
		try:
			self.video_sink.set_xwindow_id(self.window.xid)
			if self.should_show:
				self.show()
		except:
			pass
		
	
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
			return True
		else:
			return False
		#return self.discoverer.is_video
		
	def issound(self):
		if self.get_location() == None:
			return False
		ext = self.get_location().split(".").pop().lower()
		if "audio-codec" in self.tags.keys() or \
				ext in sound:
			return True
		else:
			return False
		#return self.discoverer.is_audio

class discoverer(gtk.DrawingArea,christine_gconf):
	def __init__(self):
		#print "discoverer: new instance"
		gtk.DrawingArea.__init__(self)
		christine_gconf.__init__(self)
		self.discoverer = gst.element_factory_make("playbin")
		#asink			= self.get_string("backend/audiosink")
		self.discoverer.set_property("audio-sink",gst.element_factory_make("fakesink"))
		video_sink = gst.element_factory_make("xvimagesink")
		video_sink.set_property("display","null")
		video_sink.set_property("force-aspect-ratio",True)
		self.discoverer.set_property("video-sink",video_sink)
		self.discoverer.set_property("volume",0.0)
		#self.discoverer.set_property("delay",0)
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
		self.discoverer.set_property("uri","file://%s"%file)
		self.discoverer.set_state(gst.STATE_READY)
		self.discoverer.set_state(gst.STATE_PAUSED)
		self.discoverer.set_state(gst.STATE_PLAYING)
		self.discoverer.set_state(gst.STATE_PAUSED)
		
	def found_tags_cb(self,tags):
		if len(tags.keys()) > 0:
			for i in tags.keys():
				self.tags[i] = tags[i]
		if "video-codec" or ext in CHRISTINE_VIDEO_EXT:
			self.is_video = True
		elif "audio-codec" or ext in CHRISTINE_AUDIO_EXT:
			self.is_audio = True
		#print self.tags
		
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
