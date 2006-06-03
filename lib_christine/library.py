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
from lib_christine.libs_christine import *
from lib_christine.gtk_misc import *

(PATH,NAME,TYPE,PIX,ALBUM,ARTIST,TN,SEARCH)=range(8)
(VPATH,VNAME,VPIX) = range(3)

class library(gtk_misc):
	def __init__(self,main):
		self.iters = {}
		gtk_misc.__init__(self)
		#self.player = player(self)
		self.player = play10(self)
		self.xml = glade_xml("treeview.glade","ltv")
		self.xml.signal_autoconnect(self)
		self.gconf = christine_gconf()
		self.main = main
		self.play = self.main.player
		self.tv = self.xml["ltv"]
		self.library_lib = lib_library("music")
		self.gen_model()
		filter = self.model.filter_new()
		sort = gtk.TreeModelSort(filter)
		self.tv.set_model(sort)
		self.add_columns()
		self.set_drag_n_drop()
		
	
	def gen_model(self,refresh=False):
		if not refresh:
			s = gobject.TYPE_STRING
			self.model = gtk.ListStore(s,s,s,gtk.gdk.Pixbuf,
					s,s,s,s)
		else:
			self.model.clear()
		sounds = self.library_lib.get_sounds()
		soundpix = self.gen_pixbuf("sound.png")
		soundpix = soundpix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
		videopix = self.gen_pixbuf("video.png")
		videopix = videopix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
		keys = sounds.keys()
		keys.sort()
		limit = 20
		for i in keys:
			pix = self.gen_pixbuf("blank.png")
			pix = pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
			if len (sounds[i]["name"]) > limit:
				name = sounds[i]["name"][:limit-3]+"..."
				name = sounds[i]["name"]
			else:
				name = sounds[i]["name"]
				
			if len(sounds[i]["artist"]) > limit:
				artist = sounds[i]["artist"][:limit-3]+"..."
				artist = sounds[i]["artist"]
			else:
				artist = sounds[i]["artist"]
				
			if len(sounds[i]["album"]) > limit:
				album = sounds[i]["album"][:limit-3]+"..."
				album = sounds[i]["album"]
			else:
				album = sounds[i]["album"]

			self.model.set(self.model.append(),
					NAME,name,
					PATH,i,
					TYPE,sounds[i]["type"],
					PIX, pix,
					ALBUM,album,
					ARTIST,artist,
					TN,str(sounds[i]["track_number"]),
					SEARCH,",".join([name,album,artist]))
			#self.model.foreach(self.get_last_iter)
			#self.iters.append([self.last_iter,i])

	def add_columns(self):
		render = gtk.CellRendererText()
		tv = self.tv
		tvc = gtk.TreeViewColumn
		
		pix = gtk.CellRendererPixbuf()
		icon = tvc("",pix,pixbuf=PIX)
		#icon.set_sort_column_id(TYPE)
		tv.append_column(icon)
		
		tn = tvc("Track",render,text=TN)
		tn.set_sort_column_id(TN)
		tv.append_column(tn)
	
		name = tvc("Title",render,text=NAME)
		name.set_sort_column_id(NAME)
		name.set_resizable(True)
		tv.append_column(name)

		artist = tvc("Artist",render,text=ARTIST)
		artist.set_sort_column_id(ARTIST)
		artist.set_resizable(True)
		artist.set_visible(self.gconf.get_bool("ui/show_artist"))
		tv.append_column(artist)
		
		album = tvc("Album",render,text=ALBUM)
		album.set_sort_column_id(ALBUM)
		album.set_resizable(True)
		album.set_visible(self.gconf.get_bool("ui/show_album"))
		tv.append_column(album)
		
		type = tvc("Type",render,text=TYPE)
		type.set_sort_column_id(TYPE)
		type.set_resizable(True)
		type.set_visible(self.gconf.get_bool("ui/show_type"))
		tv.append_column(type)
		
		self.gconf.notify_add("/apps/christine/ui/show_artist",self.gconf.toggle_visible,artist)
		self.gconf.notify_add("/apps/christine/ui/show_album",self.gconf.toggle_visible,album)
		self.gconf.notify_add("/apps/christine/ui/show_type",self.gconf.toggle_visible,type)
		self.discoverer = discoverer()
		self.discoverer.bus.add_watch(self.message_handler)

	def add(self,file,prepend=False):
		self.discoverer.set_location(file)
		model = self.model
		if prepend:
			iter = model.prepend()
		else:
			iter = model.append()
		self.iters[file] = iter

	def message_handler(self,a,b):
		d = self.discoverer
		t = b.type
		if t == gst.MESSAGE_TAG:
			#print a,b,d.get_location(),self.model.get_path(self.iters[d.get_location()])
			self.discoverer.found_tags_cb(b.parse_tag())
			name	= d.get_tag("title")
			album	= d.get_tag("album")
			artist	= d.get_tag("artist")
			tn		= d.get_tag("track-number")
			#if name != "":
			#	del self.discoverer
			pix = self.gen_pixbuf("blank.png")
			pix = pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
			if name == "":
				n = os.path.split(d.get_location())[1].split(".")
				name = ".".join([k for k in n[:-1]])
			model = self.model
			model.set(self.iters[d.get_location()],
						NAME,name,
						PATH,d.get_location(),
						TYPE,"sound",
						PIX, pix,
						ALBUM,album,
						ARTIST,artist,
						TN,str(tn),
						SEARCH,",".join([name,album,artist]))
		return True

	def add1(self,file,prepend=False):
		#play = play10(self)
		#play = self.player
		#play.set_location(file)
		#name   = play.get_tag("title")
		#artist = play.get_tag("artist")
		#album  = play.get_tag("album")
		name   = ""
		artist = ""
		album  = ""
		#track_number = self.play.get_tag("track-number")
		track_number = 0

		pix = self.gen_pixbuf("blank.png")
		pix = pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)

		if name == "":
			n = os.path.split(file)[1].split(".")
			name = ".".join([k for k in n[:-1]])
		model = self.model
		if prepend:
			iter = model.prepend()
		else:
			iter = model.append()
		model.set(iter,
					NAME,name,
					PATH,file,
					TYPE,"sound",
					PIX, pix,
					ALBUM,album,
					ARTIST,artist,
					TN,str(track_number),
					SEARCH,",".join([name,album,artist]))
		model.foreach(self.get_last_iter)
		self.iters.append([self.last_iter,file])
		#del play
	def get_last_iter(self,model,path,iter):
		self.last_iter = iter
	def set_tags(self):
		if len(self.iters) > 0:
			iter,path = self.iters.pop()
			print iter, path
			self.iter = iter
			self.discoverer.set_location(path)
			self.save()
		return True
			

	def remove(self,iter):
		key = self.model.get_value(iter,PATH)
		self.library_lib.remove(key)
		self.model.remove(iter)
	
	def save(self):
		'''
		Save the current library
		'''
		self.library_lib.clear()
		self.model.foreach(self.prepare_for_disk)
		self.library_lib.save()
		
		
	def prepare_for_disk(self,model,path,iter):
		name   = model.get_value(iter,NAME)
		artist = model.get_value(iter,ARTIST)
		album  = model.get_value(iter,ALBUM)
		track_number = model.get_value(iter,TN)
		path = model.get_value(iter,PATH)
		type = model.get_value(iter,TYPE)
		self.library_lib.append(path,{"name":name,
				"type":type,"artist":artist,
				"album":album,"track_number":track_number})
		
	def item_activated(self,widget,path,iter):
		model = widget.get_model()
		iter = model.get_iter(path)
		filename = model.get_value(iter,PATH)
		self.main.set_location(filename)
		#self.main.player.playit()
		#self.main.STATE_PLAYING = True
		self.main.play_button.set_active(False)
		self.main.play_button.set_active(True)
		self.main.filename = filename

	def key_press_handler(self,treeview,event):
		if event.keyval == 65535:
			selection = treeview.get_selection()
			model,iter = selection.get_selected()
			name = model.get_value(iter,NAME)
			model.remove(iter)
			self.library_lib.remove(name)
			self.save()
			
	def set_drag_n_drop(self):
		 self.tv.connect("drag_motion",self.check_contexts)
		 self.tv.connect("drag_drop",self.dnd_handler)
		 self.tv.connect("drag_data_received",self.add_it)
		 self.tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
				 [('STRING',0,0)],gtk.gdk.ACTION_COPY)
		 self.tv.connect("drag-data-get",self.drag_data_get)
	
	def drag_data_get(self,treeview,context,selection,info,timestamp):
		tsel = treeview.get_selection()
		model,iter = tsel.get_selected()
		text = model.get_value(iter,PATH)
		selection.set("STRING",8,text)
		return
		
		 

	def check_contexts(self,treeview,context,selection,info,timestamp):
		context.drag_status(gtk.gdk.ACTION_COPY,timestamp)
		return True
	def dnd_handler(self,treeview,context,selection,info,timestamp,b=None,c=None):
		'''
		'''
		tgt = treeview.drag_dest_find_target(context,[("STRING",0,0)])
		data = treeview.drag_get_data(context,tgt)
		return True
	def add_it(self,treeview,context,x,y,selection,target,timestamp):
		treeview.emit_stop_by_name("drag_data_received")
		target = treeview.drag_dest_find_target(context,[("STRING",0,0)])
		if timestamp !=0:
			#print treeview,context,x,y,selection,target,timestamp
			text = self.parse_received_data(selection.get_text())
			#print text
			if len(text)>0:
				install_gui(text,self)
		return True

class queue(gtk_misc):
	def __init__(self,main):
		gtk_misc.__init__(self)
		self.main = main
		self.library = lib_library("queue")
		self.xml = glade_xml("treeview.glade","ltv")
		self.xml.signal_autoconnect(self)
		self.treeview= self.xml["ltv"]
		self.gen_model()
		self.treeview.set_model(self.model)
		self.add_columns()
		self.set_drag_n_drop()
		
	def gen_model(self,refresh=False):
		if refresh:
			self.model.clear()
		else:
			s = gobject.TYPE_STRING
			p = gtk.gdk.Pixbuf
			self.model = gtk.ListStore(s,s,s)
		keys = self.library.keys()
		print self.library.files
		keys.sort()
		for i in keys:
			print i, self.library[i]["name"]
			iter = self.model.append()
			self.model.set(iter,
					PATH,self.library[i]["path"],
					NAME,self.library[i]["name"],
					TYPE,self.library[i]["type"])
	
	def add(self,filename,prepend=False):
		file = os.path.split(filename)[1]
		name = ".".join(k for k in file.split(".")[:-1])
		if prepend:
			iter = self.model.prepend()
		else:
			iter = self.model.append()
		self.model.set(iter,
				PATH,filename,
				NAME,name,
				TYPE,"sound")

		#self.discoverer = gst.extend.discoverer.Discoverer(filename)
		#self.discoverer.connect("discovered",self.add1,filename,iter,prepend)
		#gobject.timeout_add(100,self.print_discover)
		#gobject.timeout_add(500,self.add1,filename,prepend)

#	def print_discover(self,widget=None,b=None):
#		#print widget,b
#		self.discoverer.discover()
#		#print self.discoverer.print_info()
#		print "tags:",self.discoverer.tags
#		self.tags = self.discoverer.tags
#		if len(self.discoverer.tags.keys()):
#			return False
#		return True

	def add1(self,widget,b,filename,iter,prepend=False):
		try:
			name = self.tags["title"]
		except:
			name = ".".join(k for k in file.split(".")[:-1])
		if self.discoverer.is_audio:
			type1 = "sound"
		else:
			type1 = "video"
		pix = self.gen_pixbuf(type1+".png")
		pix = pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
		file = os.path.split(filename)[1]
		self.model.set(iter,
				PATH,filename,
				NAME,name,
				TYPE,"sound")
		self.save()
	
	def add_columns(self):
		render = gtk.CellRendererText()
		tv = self.treeview
		pix = gtk.CellRendererPixbuf()
		icon = gtk.TreeViewColumn("",pix,pixbuf=PIX)
		icon.set_sort_column_id(TYPE)
		#tv.append_column(icon)
		name = gtk.TreeViewColumn("Title",render,text=NAME)
		name.set_sort_column_id(NAME)
		tv.append_column(name)

	def remove(self,iter):
		path = self.model.get_value(iter,PATH)
		self.model.remove(iter)
		self.library.files = {}
		self.save()
	
	def save(self):
		'''
		Save the current library
		'''
		self.pos = 0
		self.model.foreach(self.prepare_for_disk)
		self.library.save()
		
		
	def prepare_for_disk(self,model,path,iter):
		name = self.model.get_value(iter,NAME)
		path = self.model.get_value(iter,PATH)
		self.library.append(self.pos,{"path":path,"name":name,"type":"sound","extra":[]})
		self.pos += 1
		
	def item_activated(self,widget,path,iter):
		model = widget.get_model()
		iter = model.get_iter(path)
		filename = model.get_value(iter,PATH)
		self.main.set_location(filename)
		self.main.player.set_location(filename)
		self.main.play_button.set_active(False)
		self.main.play_button.set_active(True)
		self.main.filename = filename
	
	def key_press_handler(self,widget,event,key):
		print widget,event,key
	
	def set_drag_n_drop(self):
		 self.treeview.connect("drag_motion",self.check_contexts)
		 self.treeview.connect("drag_drop",self.dnd_handler)
		 self.treeview.connect("drag_data_received",self.add_it)

	def check_contexts(self,treeview,context,selection,info,timestamp):
		context.drag_status(gtk.gdk.ACTION_COPY,timestamp)
		print selection.get_text()
		return True

	def dnd_handler(self,treeview,context,selection,info,timestamp,b=None,c=None):
		'''
		'''
		tgt = treeview.drag_dest_find_target(context,[("STRING",0,0),("STRING",8,0)])
		data = treeview.drag_get_data(context,tgt)
		return True
	
	def add_it(self,treeview,context,x,y,selection,target,timestamp):
		treeview.emit_stop_by_name("drag_data_received")
		target = treeview.drag_dest_find_target(context,[("STRING",0,0)])
		if timestamp !=0:
			text = self.parse_received_data(selection.get_text())
			if len(text)>0:
				for i in text:
					print i
					#self.add(i)
		return True

	def parse_received_data(self,text):
		'''
		Parse the text and return a tuple with the text.
		'''
		result = []
		text = str(text)
		te = text.split("\n")
		for i in te:
			i = i.replace("\r"," ").strip()
			ext = i.split(".").pop()
			if ext in sound or \
					ext in video:
				result.append(i)
		return result
		

class mini_lists:
	def __init__(self,header,first_element):
		self.xml = glade_xml("treeview.glade","ltv")
		self.treeview = self.xml["ltv"]
		self.header = header
		self.first_element = first_element
		self.list = []
		self.gen_model()
		self.add_column()
		filter = self.model.filter_new()
		filter.set_visible_func(self.filter)
		self.treeview.set_model(filter)
		
	def gen_model(self,refresh=False):
		if refresh:
			self.model.clear()
		else:
			self.model = gtk.ListStore(gobject.TYPE_STRING)
		self.add(self.first_element)
			
	def add(self,artist):
		iter = self.model.append()
		self.model.set(iter,
				0,artist)
		self.list.append(artist)
		
	def add_column(self):
		artist = gtk.TreeViewColumn(self.header,
				gtk.CellRendererText(),
				text=0)
		self.treeview.append_column(artist)
		
	def filter(self,model,iter,text=""):
		value = model.get_value(iter,0)
		if value == text:
			return True
		else:
			return False
	

#
# code below this comment is deprecated
#
#
class video_library(gtk_misc):
	def __init__(self,main):
		gtk_misc.__init__(self)
		self.main = main
		self.xml = glade_xml("icon_view.glade","iconv")
		self.xml.signal_autoconnect(self)
		self.iv = self.xml["iconv"]
		self.library = lib_library("video")
		self.gen_model()
		self.iv.set_model(self.model)
		self.add_columns()
		
	def item_activated(self,widget,path):
		model = self.model
		iter = model.get_iter(path)
		filename = model.get_value(iter,VPATH)
		self.main.set_location(filename)
		self.main.play()
		

	def gen_model(self,refresh=False):
		s = gobject.TYPE_STRING
		if refresh:
			self.model.clear()
		else:
			self.model = gtk.ListStore(s,s,gtk.gdk.Pixbuf)
		videos = self.library.get_videos()
		for i in videos.keys():
			self.model.set(self.model.append(),
					VPIX, self.gen_pixbuf("video.png"),
					VNAME,i,
					PATH,videos[i]["path"])
					
		
	def add(self,file):
		model = self.model
		iter = model.append()
		path,name = os.path.split(file)
		model.set(iter,
				VNAME,name,
				VPATH,file,
				VPIX, self.gen_pixbuf("video.png"))

	def add_columns(self):
		self.iv.set_pixbuf_column(VPIX)
		self.iv.set_text_column(VNAME)
	
	def save(self):
		self.model.foreach(self.prepare_for_disk)
		self.library.save()

	def prepare_for_disk(self,model,path,iter):
		name = model.get_value(iter,VNAME)
		path = model.get_value(iter,VPATH)
		pix  = model.get_value(iter,VPIX)
		self.library.append(name,{"path":path,"type":"video","extra":[]})
	
