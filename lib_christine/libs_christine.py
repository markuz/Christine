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


import os,gtk,gobject
import cPickle as pickle
import gst
version = gst.version()
if version[1] == 8:
	import gst.play
elif version[1] == 10:
	import gst.extend.discoverer
import gst.interfaces

from lib_christine.gtk_misc import *




GST_DELAY = 500
wdir = os.environ["HOME"]+"/.christine/"
sound = ["mp3","ogg","wma"]
video = ["mpg","mpeg","mpe","avi"]

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
		try:
			f =	open(os.path.join(wdir,list),"r")
			self.files = pickle.load(f)
			f.close()
		except:
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
			if self.files[i]["type"] == "sound":
				a[i] = self.files[i]
		return a

	def get_videos(self):
		a = {}
		for i in self.keys():
			if self.files[i]["type"] == "video":
				a[i] = self.files[i]
		return a

class player(gtk.DrawingArea):
	def __init__(self,parent):
		self.should_show = False
		gtk.DrawingArea.__init__(self)
		self.main = parent
		self.tags = {}
		self.connect('destroy', self.destroy_cb)
		self.connect('expose-event', self.expose_cb)
		#self.connect("event",self.event)
		self.set_size_request(200,200)
		self.play = gst.play.Play()
		clock = self.play.get_clock()
		self.play.set_clock(clock)
		self.play.connect("have-video-size",self.size_request)
		self.play.connect("error",self.error_handler)

		self.gconf = christine_gconf()

		asink = self.gconf.get_string("backend/audiosink")
		self.audio_sink = gst.element_factory_make(asink)
		self.audio_sink.connect("found-tag",self.found_tag_cb)
		if asink == "alsasink":
			self.audio_sink.set_property('device', 'hw:0')

		videosink = self.gconf.get_string("backend/videosink")
		aspect = self.gconf.get_string("backend/video-aspect-ratio")
		self.video_sink = gst.element_factory_make(videosink)
		self.video_sink.set_property("pixel-aspect-ratio",aspect)
		self.play.set_video_sink(self.video_sink)

		
		filesrc = gst.element_factory_make("filesrc")
		self.play.set_data_src(filesrc)
		self.play.set_audio_sink(self.audio_sink)

		vis = self.gconf.get_string("backend/vis-plugin")
		self.visualization = gst.element_factory_make(vis)
		self.set_visualization_visible(True)
		self.set_visualization_visible()

		self.volume = self.play.get_list()[0]
		vol = self.gconf.get_float("backend/volume")
		self.volume.set_property("volume",vol)

		#gobject.timeout_add(1000,self.sync)
	
	def set_visualization_visible(self,active=False):
		self.should_show = active
		if active:
			self.play.get_list()[0].set_property("vis-plugin",self.visualization)
			self.show()
		else:
			self.play.get_list()[0].set_property("vis-plugin",None)
			try:
				if self.type == "sound":
					self.hide()
			except:
				self.hide()
			
	def __create_fakeplay(self):
		self.__fakeplay = gst.play.Play()
		vsink = gst.element_factory_make("xvimagesink")
		self.__fakeplay.enable_threadsafe_properties()
		self.__fakeplay.connect("found-tag",self.found_tag_cb)
		self.__fakeplay.set_data_src(gst.element_factory_make("filesrc"))
		self.__fakeplay.set_audio_sink(gst.element_factory_make("fakesink"))
		self.__fakeplay.set_video_sink(vsink)
		vsink.set_xwindow_id(0L)
		
	def set_volume(self,volume):
		if volume < 0.0:
			volume = 0.0
		elif volume > 1.0:
			volume = 1.0
		self.volume.set_property("volume",volume)
		
	def found_tag_cb(self,play, src, tags):
		if len(tags.keys()) > 0:
			for i in tags.keys():
				self.tags[i] = tags[i]
	
	def sync(self):
		self.play.sync_children_state()
		return True
		

	def error_handler(self,a,b,c,d):
		print self.play.get_location()
		print a,b,c,d,a.get_state()
		#print "Hooo., I'm dead.."
		
	def size_request(self,a,b,c):
		self.size = [b,c]
		self.set_size_request(b,c)
		
	
	def set_location(self,filename):
		self.tags = {}
		ext = filename.split(".").pop()
		print filename
		#self.stop()
		self.play.set_location(filename)
		ext = filename.split(".").pop()
		if not ext in video:
			self.__create_fakeplay()
			self.__fakeplay.set_location(filename)
			self.__fakeplay.set_state(gst.STATE_PLAYING)
			self.__fakeplay.set_state(gst.STATE_PAUSED)
			self.__fakeplay.set_state(gst.STATE_NULL)
		else:
			title = ".".join([k for k in os.path.split(filename)[1].split(".")[:-1]])
			self.tags = {"title":title}
		self.get_type()
	

	def get_tag(self,key):
		try:
			return self.tags[key]
		except:
			return ""
	
	def get_location(self):
		return self.play.get_location()

	def get_type(self):
		if self.isvideo():
			self.type = "video"
		elif self.issound():
			self.type = "sound"
		else:
			raise TypeError,"Not an known video or sound"
		
	def playit(self):
		if self.get_location() != None:
			self.play.set_state(gst.STATE_PLAYING)
		
	def pause(self,a=None):
		self.play.set_state(gst.STATE_PAUSED)
		
	def stop (self,a=None):
		#self.hide()
		self.play.set_state(gst.STATE_NULL)
		#self.main.scale.set_value(0)
	
	def nano2str(self,nanos):
		ts = nanos / gst.SECOND
		return '%02d:%02d:%02d.%06d' % (ts / 3600,
				ts / 60,ts % 60, nanos % gst.SECOND)
		#print ts

	def destroy_cb(self, da):
		#self.error_handler("","")
		self.video_sink.set_xwindow_id(0L)
		
	def expose_cb(self, window, event=None):
		self.video_sink.set_xwindow_id(self.window.xid)
		if self.should_show:
			self.show()
		
	#def event(self,window,event):
	#	print event.type
	#	self.show()
	
	def seek_to(self,sec):
		sec = long(sec)*gst.SECOND
		self.audio_sink.seek(gst.FORMAT_TIME|gst.SEEK_FLAG_FLUSH
				|gst.SEEK_METHOD_SET,sec)
		self.video_sink.seek(gst.FORMAT_TIME|gst.SEEK_FLAG_FLUSH
				|gst.SEEK_METHOD_SET,sec)


	def isvideo(self):
		ext = self.get_location().split(".").pop().lower()
		if "video-codec" in self.tags.keys() or \
			ext in video:
			return True
		else:
			return False
		
	def issound(self):
		ext = self.get_location().split(".").pop().lower()
		if "audio-codec" in self.tags.keys() or \
				ext in sound:
			return True
		else:
			return False
	

	def gstmain(self):
		gst.main()
		return False

	def quit(self):
		gst.main_quit()


		
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
		
		#self.vis_plugin = gst.element_factory_make("goom")
		#self.playbin.set_property("vis-plugin",self.vis_plugin)

		#self.bus.add_watch(self.error_handler)
		#self.playbin.connect("error",self.error_handler)
		asink			= self.get_string("backend/audiosink")
		self.audio_sink = gst.element_factory_make(asink)
		#print "asink",asink
		if asink == "alsasink":
			self.audio_sink.set_property("device","hw:0")
		vsink			= self.get_string("backend/videosink") 
		#print "vsink:",vsink
		aspect_ratio	= self.get_string("backend/aspect-ratio")
		self.video_sink = gst.element_factory_make(vsink)
		if aspect_ratio != None:
			self.video_sink.set_property("pixel-aspect-ratio",aspect_ratio)
		vsink			= self.get_string("backend/vis-plugin") 
		self.__connect()
		self.query_duration = self.playbin.query_duration
		self.query_position = self.playbin.query_position

		
	def __connect(self):
		self.playbin.set_property("video-sink",self.video_sink)
		self.playbin.set_property("audio-sink",self.audio_sink)

	def set_location(self,file):
		print "self.tags={}"
		self.tags = {}
		if os.path.isfile(file):
			nfile = "file://"+file
			#print "nfile:",nfile
			print "self.playbin.set_property(\"uri\",nfile)"
			self.playbin.set_property("uri",nfile)
			#self.discoverer = gst.extend.discoverer.Discoverer(file)
			#gobject.timeout_add(500,self.print_discover)
			print "self.pause()"
			self.pause()
			print "set_location is done"
		else:
			print file
			error("file %s not found"%os.path.split(file)[1])
		#print "set_location check:",self.playbin.get_property("uri")
		self.get_type()
			
	def print_discover(self,widget=None,b=None):
		#print widget,b
		self.discoverer.discover()
		#print self.discoverer.print_info()
		print "tags:",self.discoverer.tags
		self.tags = self.discoverer.tags
		if len(self.discoverer.tags.keys()):
			return False
		return True

	def playit(self):
		self.playbin.set_state(gst.STATE_PLAYING)
		#gobject.timeout_add(1000,self.check)
	
	def check(self):
		print self.playbin.get_property("queue-size")
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
		if active:
			#self.playbin.set_property("vis-plugin",self.vis_plugin)
			self.show()
		else:
			#self.playbin.set_property("vis-plugin",None)
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
		print __name__,"fount_tags_cb",self.tags

	def get_location(self):
		path = self.playbin.get_property("uri")
		if path != None:
			path = path[7:]
		else:
			path = None
		print "player.get_location:",path
		return path

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
		
	def expose_cb(self, window, event=None):
		self.video_sink.set_xwindow_id(self.window.xid)
		if self.should_show:
			self.show()
		
	
	def seek_to(self,sec):
		sec = long(sec)*gst.SECOND
		self.playbin.seek(1.0,gst.FORMAT_TIME,gst.SEEK_FLAG_FLUSH,
				gst.SEEK_TYPE_SET,sec,gst.SEEK_TYPE_NONE,-1)

		#self.audio_sink.seek(1.0,gst.FORMAT_TIME,gst.SEEK_FLAG_FLUSH,
		#		gst.SEEK_TYPE_SET,sec,gst.SEEK_TYPE_NONE,-1)
		#self.video_sink.seek(1.0,gst.FORMAT_TIME,gst.SEEK_FLAG_FLUSH,
		#		gst.SEEK_TYPE_SET,sec,gst.SEEK_TYPE_NONE,-1)
		#self.video_sink.seek(gst.FORMAT_TIME|gst.SEEK_FLAG_FLUSH
		#		|gst.SEEK_METHOD_SET,sec)


	def isvideo(self):
		ext = self.get_location().split(".").pop().lower()
		if "video-codec" in self.tags.keys() or \
			ext in video:
			return True
		else:
			return False
		#return self.discoverer.is_video
		
	def issound(self):
		ext = self.get_location().split(".").pop().lower()
		if "audio-codec" in self.tags.keys() or \
				ext in sound:
			return True
		else:
			return False
		#return self.discoverer.is_audio

class discoverer:
	def __init__(self):
		print "discoverer: new instance"
		self.discoverer = gst.element_factory_make("playbin")
		self.discoverer.set_property("audio-sink",gst.element_factory_make("esdsink"))
		self.discoverer.set_property("video-sink",gst.element_factory_make("xvimagesink"))
		self.discoverer.set_property("volume",0.0)
		#self.discoverer.set_property("delay",0)
		self.bus = self.discoverer.get_bus()
	
	def set_location(self,file):
		self.tags = {}
		self.discoverer.set_property("uri","file://%s"%file)
		self.discoverer.set_state(gst.STATE_READY)
		self.discoverer.set_state(gst.STATE_PAUSED)
		self.discoverer.set_state(gst.STATE_PLAYING)
		self.discoverer.set_state(gst.STATE_PAUSED)
		#gobject.timeout_add(100,self.set_null)



	def found_tags_cb(self,tags):
		if len(tags.keys()) > 0:
			for i in tags.keys():
				self.tags[i] = tags[i]
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
