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


import os,gtk,gobject,sys,pango
import cPickle as pickle
import gst, gst.interfaces
from libchristine.libs_christine import *
from libchristine.GtkMisc import *
from libchristine.Discoverer import *
from libchristine.Translator import *
from libchristine import clibrary
from libchristine.ChristineGConf import *
from libchristine.Share import *
import time

(PATH,
NAME,
TYPE,
PIX,
ALBUM,
ARTIST,
TN,
SEARCH,
PLAY_COUNT,
TIME,
GENRE) = range(11)

(VPATH,
VNAME,
VPIX) = range(3)


##
## Since library and queue are more or less the same 
## thing. I guess we need to use a base class for 
## both lists (and other lists)
##

class library(GtkMisc,gtk.DrawingArea):
	def __init__(self):
		'''
		Constructor, load the 
		glade ui description for a simple treeview
		and set some class variables
		'''
		self.iters = {}
		GtkMisc.__init__(self)
		self.__Share = Share()
		gtk.DrawingArea.__init__(self)
		self.__xml = self.__Share.getTemplate("TreeViewSources","treeview")
		gobject.signal_new("tags-found",self,
				gobject.SIGNAL_RUN_LAST,
				gobject.TYPE_NONE,
				(gobject.TYPE_PYOBJECT,))
		self.__xml.signal_autoconnect(self)
		self.gconf = ChristineGConf()
		self.tv = self.__xml["treeview"]
		self.library_lib = lib_library("music")
		self.gen_model()
		filter = self.model.filter_new()
		sort = gtk.TreeModelSort(filter)
		self.tv.set_model(sort)
		self.__add_columns()
		self.set_drag_n_drop()
		self.blank_pix = self.gen_pixbuf("blank.png")
		self.blank_pix = self.blank_pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
		self.CURRENT_ITER = self.model.get_iter_first()
		#gobject.timeout_add(1000,self.update_values)
	
	#def update_values(self):
	#	try:
	#		self.CURRENT_ITER = self.model.iter_next(self.CURRENT_ITER)
	#		path = self.model.get(self.CURRENT_ITER,PATH)
	#		self.discoverer.setLocation(path)
	#		self.iters[self.discoverer.getLocation()] = self.CURRENT_ITER
	#		print locals()
	#	except:
	#		self.CURRENT_ITER = self.model.get_iter_first()
	#	print self.discoverer.getLocation()
	#	return True
	
	def gen_model(self,refresh=False):
		if not refresh:
			s = gobject.TYPE_STRING
			i = gobject.TYPE_INT
			self.model = gtk.ListStore(
					gobject.TYPE_STRING, #path
					gobject.TYPE_STRING, #name
					gobject.TYPE_STRING, #type
					gtk.gdk.Pixbuf, #Pix
					gobject.TYPE_STRING, #album
					gobject.TYPE_STRING, #artist
					int, #Track Number
					gobject.TYPE_STRING, #search
					int, #play count
					gobject.TYPE_STRING, #time
					gobject.TYPE_STRING) #Genre
		else:
			self.model.clear()
		if "--plibrary" in sys.argv:
			#print "using python library code,"
			self.__pgen_model()
		else:
			#print "using C library code,"
			#print "if you want to use Python code run christine with"
			#print "--plibrary option"
			self.__cgen_model()

	def __pgen_model(self):
		append = self.model.append
		sounds = self.library_lib.get_sounds()
		keys = sounds.keys()
		keys.sort()
		limit = 20
		pix = self.gen_pixbuf("blank.png")
		pix = pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
		for i in keys:
			if not sounds[i].has_key("play_count"):
				sounds[i]["play_count"] = 0

			if not sounds[i].has_key("duration"):
				sounds[i]["duration"] = "00:00"
			if not sounds[i].has_key("genre"):
				sounds[i]["genre"] = ""

			self.model.set(append(),
					NAME,sounds[i]["name"],
					PATH,i,
					TYPE,sounds[i]["type"],
					PIX, pix,
					ALBUM,sounds[i]["album"],
					ARTIST,sounds[i]["artist"],
					TN,str(sounds[i]["track_number"]),
					SEARCH,",".join([sounds[i]["name"],sounds[i]["album"],
									sounds[i]["artist"]]),
					PLAY_COUNT,sounds[i]["play_count"],
					TIME,sounds[i]["duration"],
					GENRE, sounds[i]["genre"])
		#self.tv.freeze_child_notify()

	def __cgen_model(self):
		append = self.model.append
		sounds = self.library_lib.get_all()
		clibrary.set_create_iter(append)
		clibrary.set_set(self.model.set)
		clibrary.fill_model(sounds)
		return True

	def __add_columns(self):
		render = gtk.CellRendererText()
		render.set_property("ellipsize",pango.ELLIPSIZE_END)
		tv = self.tv
		tvc = gtk.TreeViewColumn
		
		tn = tvc(translate("T#"),render,text=TN)
		tn.set_sort_column_id(TN)
		tn.set_visible(self.gconf.getBool("ui/show_tn"))
		tv.append_column(tn)
	
		pix = gtk.CellRendererPixbuf()
		name = tvc(translate("Title"))
		name.set_sort_column_id(NAME)
		name.set_resizable(True)
		name.set_fixed_width(250)
		name.set_property("sizing",gtk.TREE_VIEW_COLUMN_FIXED)
		name.pack_start(pix,False)
		rtext = gtk.CellRendererText()
		rtext.set_property("ellipsize",pango.ELLIPSIZE_END)
		name.pack_start(rtext,True)
		name.add_attribute(pix,"pixbuf",PIX)
		name.add_attribute(rtext,"text",NAME)
		tv.append_column(name)
		

		artist = tvc(translate("Artist"),render,text=ARTIST)
		artist.set_sort_column_id(ARTIST)
		artist.set_resizable(True)
		artist.set_fixed_width(150)
		artist.set_property("sizing",gtk.TREE_VIEW_COLUMN_FIXED)
		artist.set_visible(self.gconf.getBool("ui/show_artist"))
		tv.append_column(artist)
		
		album = tvc(translate("Album"),render,text=ALBUM)
		album.set_sort_column_id(ALBUM)
		album.set_resizable(True)
		album.set_fixed_width(150)
		album.set_property("sizing",gtk.TREE_VIEW_COLUMN_FIXED)
		album.set_visible(self.gconf.getBool("ui/show_album"))
		tv.append_column(album)
		
		type = tvc(translate("Type"),render,text=TYPE)
		type.set_sort_column_id(TYPE)
		type.set_resizable(True)
		type.set_visible(self.gconf.getBool("ui/show_type"))
		tv.append_column(type)

		play = tvc(translate("Count"),render,text=PLAY_COUNT)
		play.set_sort_column_id(PLAY_COUNT)
		play.set_resizable(True)
		play.set_visible(self.gconf.getBool("ui/show_play_count"))
		tv.append_column(play)

		length = tvc(translate("Lenght"),render,text=TIME)
		length.set_sort_column_id(TIME)
		length.set_resizable(True)
		length.set_visible(self.gconf.getBool("ui/show_length"))
		tv.append_column(length)

		genre = tvc(translate("Genre"),render,text=GENRE)
		genre.set_sort_column_id(GENRE)
		genre.set_resizable(True)
		genre.set_visible(self.gconf.getBool("ui/show_genre"))
		tv.append_column(genre)


		self.gconf.notifyAdd("/apps/christine/ui/show_artist",self.gconf.toggleVisible,artist)
		self.gconf.notifyAdd("/apps/christine/ui/show_album",self.gconf.toggleVisible,album)
		self.gconf.notifyAdd("/apps/christine/ui/show_type",self.gconf.toggleVisible,type)
		self.gconf.notifyAdd("/apps/christine/ui/show_tn",self.gconf.toggleVisible,tn)
		self.gconf.notifyAdd("/apps/christine/ui/show_play_count",self.gconf.toggleVisible,play)
		self.gconf.notifyAdd("/apps/christine/ui/show_length",self.gconf.toggleVisible,length)
		self.gconf.notifyAdd("/apps/christine/ui/show_genre",self.gconf.toggleVisible,genre)
		self.discoverer = Discoverer()
		self.discoverer.Bus.add_watch(self.message_handler)
		self.discoverer2 = Discoverer()
		self.discoverer2.Bus.add_watch(self.message_handler)
		gobject.timeout_add(100,self.stream_length,None,1)
		gobject.timeout_add(200,self.stream_length,None,2)

	def add(self,file,prepend=False,n=1):
		#if n == 1:
		self.discoverer.setLocation(file)
		#else:
		#	self.discoverer2.setLocation(file)
		if type(file) == type(()):
			file = file[0]
		if not os.path.isfile(file):
			return False
		if prepend:
			iter = self.model.prepend()
		else:
			iter = self.model.append()
		name = os.path.split(file)[1]
		if type(name) == type(()):
			name = name[0]
		self.model.set(iter,
				NAME,name,
				PIX,self.blank_pix,
				PATH,file,
				GENRE,"")
		self.iters[file] = iter
		#print file, self.model.getValue(iter,PATH),self.iters[file]
		#gobject.timeout_add(3000,self.NEXT)
		path = self.model.get_path(iter)
		self.tv.scroll_to_cell(path,None,True,0.5,0.5)
		return False

	def NEXT(self):
		print "NEXT"
		self.emit("tags-found",self)

	def message_handler(self,bus,b):
		if bus == self.discoverer.Bus:
			d = self.discoverer
		else:
			d = self.discoverer2
		t = b.type
		if t == gst.MESSAGE_TAG:
			iter = self.iters[d.getLocation()]
			name = self.model.get_value(iter,NAME)
			if name == os.path.split(d.getLocation()[1]):
				return True
			d.callbackFoundTags(b.parse_tag())
			name	= d.getTag("title")
			album	= d.getTag("album")
			artist	= d.getTag("artist")
			tn		= d.getTag("track-number")
			genre	= d.getTag("genre")
			if name == "":
				n = os.path.split(d.getLocation())[1].split(".")
				name = ".".join([k for k in n[:-1]])
			model = self.model
			if d.getTag("video-codec") != "" or \
					os.path.splitext(d.getLocation())[1] in CHRISTINE_VIDEO_EXT:
				t = "video"
			else:
				t = "audio"
					
			if type(tn) == type(""):
				if not tn.isdigit():
					tn = 0
				else:
					tn = int(tn)
			self.model.set(self.iters[d.getLocation()],
					NAME,name,
					TYPE,t,
					ALBUM,album,
					ARTIST,artist,
					TN,tn,
					SEARCH,",".join([name,album,artist]),
					PLAY_COUNT,0,
					GENRE,genre)

			while gtk.events_pending():
				     gtk.mainiteration(False)
			time.sleep(0.005)
			#gobject.timeout_add(150,self.emit_signal,"tags-found")
			#if not gtk.events_pending():
			self.emit_signal("tags-found")
		if t == gst.MESSAGE_ERROR:
			print b.parse_error()
		return True

	def emit_signal(self,signal):
		self.emit(signal,self)
		return False

	def stream_length(self,widget=None,n=1):
		if n==1:
			d = self.discoverer
		else:
			d = self.discoverer2
		try: 
			total = d.query_duration(gst.FORMAT_TIME)[0]
			ts = total/gst.SECOND
			text = "%02d:%02d"%divmod(ts,60)
			self.model.set(self.iters[d.getLocation()],
					TIME,text)
		except gst.QueryError:
			#d.setLocation(d.getLocation())
			pass
		return True


	def remove(self,iter):
		'''
		Remove the selected iter from the library.
		'''
		key = self.model.get_value(iter,PATH)
		self.library_lib.remove(key)
		self.model.remove(iter)
	
	def save(self):
		'''
		Save the current library
		'''
		self.library_lib.clear()
		self.append = self.library_lib.append
		self.model.foreach(self.prepare_for_disk)
		self.library_lib.save()
		
	#pdb.set_trace()
	def prepare_for_disk(self,model,path,iter):
		(name,
		artist,
		album,
		track_number,
		path,
		type,
		pc,
		duration,
		genre) = model.get(iter,NAME,
					ARTIST,
					ALBUM,
					TN,
					PATH,
					TYPE,
					PLAY_COUNT,
					TIME,
					GENRE)
		self.append(path,{"name":name,
				"type":type,"artist":artist,
				"album":album,"track_number":track_number,
				"play_count":pc,
				"duration":duration,
				"genre":genre})
		

	def key_press_handler(self,treeview,event):
		if event.keyval == 65535:
			selection = treeview.get_selection()
			model,iter = selection.get_selected()
			name = model.getValue(iter,NAME)
			model.remove(iter)
			self.library_lib.remove(name)
			self.save()
			
	
	# Need some help in the next functions
	# They need to be retouched to work fine.
	def set_drag_n_drop(self):
		 self.tv.connect("drag_motion",self.check_contexts)
		 self.tv.connect("drag_drop",self.dnd_handler)
		 self.tv.connect("drag_data_received",self.add_it)
		 self.tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
				 [('STRING',0,0)],gtk.gdk.ACTION_COPY)
		 self.tv.connect("drag-data-get",self.drag_data_get)
	
	def drag_data_get(self,
			treeview,
			context,
			selection,
			info,
			timestamp):
		tsel = treeview.get_selection()
		model,iter = tsel.get_selected()
		text = model.getValue(iter,PATH)
		selection.set("STRING",8,text)
		return
		
	def check_contexts(self,
			treeview,
			context,
			selection,
			info,
			timestamp):
		context.drag_status(gtk.gdk.ACTION_COPY,timestamp)
		return True

	def dnd_handler(self,
			treeview,
			context,
			selection,
			info,
			timestamp,
			b=None,
			c=None):
		tgt = treeview.drag_dest_find_target(context,[("STRING",0,0)])
		data = treeview.drag_get_data(context,tgt)
		return True

	def add_it(self,
			treeview,
			context,
			x,
			y,
			selection,
			target,
			timestamp):
		treeview.emit_stop_by_name("drag_data_received")
		target = treeview.drag_dest_find_target(context,[("STRING",0,0)])
		if timestamp !=0:
			#print treeview,context,x,y,selection,target,timestamp
			text = self.parse_received_data(selection.get_text())
			#print text
			if len(text)>0:
				install_gui(text,self)
		return True

	def delete_from_disk(self,iter):
		dialog = glade_xml("delete_file_from_disk_dialog.glade")["dialog"]
		response = dialog.run()
		path = self.model.getValue(iter,PATH)
		if response == -5:
			try:
				os.unlink(path)
				self.remove(iter)
				self.save()
			except IOError:
				error("cannot delete file: %s"%path)
		dialog.destroy()

