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
from libchristine.Share import *
from libchristine.Tagger import *
from libchristine import clibrary
#import pdb

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
		GENRE)=xrange(11)

(VPATH,
		VNAME,
		VPIX) = xrange(3)

QUEUE_TARGETS = [
		('MY_TREE_MODEL_ROW',gtk.TARGET_SAME_WIDGET,0),
		('text/plain',0,1),
		('TEXT',0,2),
		('STRING',0,3)
		]


class queue(GtkMisc,gtk.DrawingArea):
	def __init__(self):
		gtk.DrawingArea.__init__(self)
		GtkMisc.__init__(self)
		self.__Share = Share()
		self.iters = {}
		#self.discoverer = Discoverer()
		#self.discoverer.Bus.add_watch(self.message_handler)
		self.library = lib_library("queue")
		self.__xml = self.__Share.getTemplate("TreeViewSources","treeview")
		self.__xml.signal_autoconnect(self)
		self.treeview = self.__xml["treeview"]
		self.treeview.set_headers_visible(False)
		#self.treeview.set_reorderable(True)
		gobject
		self.gen_model()
		self.treeview.set_model(self.model)
		self.__add_columns()
		self.set_drag_n_drop()
	
		
	def gen_model(self,refresh=False):
		if refresh:
			self.model.clear()
		else:
			s = gobject.TYPE_STRING
			p = gtk.gdk.Pixbuf
			self.model = gtk.ListStore(s,s,s)
		keys = self.library.keys()
		keys.sort()
		for i in keys:
			print i, self.library[i]["name"]
			iter = self.model.append()
			self.model.set(iter,
					PATH,self.library[i]["path"],
					NAME,self.library[i]["name"],
					TYPE,self.library[i]["type"])
			
	def add(self,file,prepend=False):
		print "add:",file
		self.file = file
		if not os.path.isfile(file):
			print "No es un archivo"
			return False
		model = self.model
		if prepend:
			iter = model.prepend()
		else:
			iter = model.append()
		try:
			tagger = Tagger(file)
			tags = tagger.readTags()
		except:
			self.emit_signal("tags-found!")
			return True
		#print a,b,d.getLocation(),self.model.get_path(self.iters[d.getLocation()])
		name	= self.strip_XML_entities(tags["title"])
		album	= self.strip_XML_entities(tags["album"])
		artist	= self.strip_XML_entities(tags["artist"])
		tn		= tags["track"]
		if name == "":
			n = os.path.split(self.file)[1].split(".")
			name = ".".join([k for k in n[:-1]])
		name = "<b><i>%s</i></b>"%name
		name = self.strip_XML_entities(name)
		if album !="":
			name += "\n from <i>%s</i>"%album
		if artist != "":
			name += "\n by <i>%s</i>"%artist
		model.set(iter,
					PATH,file,
					NAME,name,
					TYPE,"sound")

	def __add_columns(self):
		render = gtk.CellRendererText()
		tv = self.treeview
		pix = gtk.CellRendererPixbuf()
		icon = gtk.TreeViewColumn("",pix,pixbuf=PIX)
		icon.set_sort_column_id(TYPE)
		#tv.append_column(icon)
		name = gtk.TreeViewColumn(translate("Queue"),render,markup=NAME)
		name.set_sort_column_id(NAME)
		tv.append_column(name)

	def remove(self,iter):
		path = self.model.get_value(iter,PATH)
		self.model.remove(iter)
		self.library.clear()
		self.save()
	
	def save(self):
		'''
		Save the current library
		'''
		print "queue save"
		self.pos = 0
		self.model.foreach(self.prepare_for_disk)
		self.library.save()
		
		
	def prepare_for_disk(self,model,path,iter):
		name = self.model.get_value(iter,NAME)
		path = self.model.get_value(iter,PATH)
		self.library.append(self.pos,{"path":path,"name":name,"type":"sound","extra":[]})
		self.pos += 1
		
	#def item_activated(self,widget,path,iter):
	#	model = widget.get_model()
	#	iter = model.get_iter(path)
	#	filename = model.get_value(iter,PATH)
	#	self.main.setLocation(filename)
	#	self.main.player.setLocation(filename)
	#	self.main.play_button.set_active(False)
	#	self.main.play_button.set_active(True)
	#	self.main.filename = filename
	
	def key_press_handler(self,widget,event,key):
		print widget,event,key
	
	def set_drag_n_drop(self):
	### FIXME For some reason this thing doesn't work!!! ###
		self.treeview.enable_model_drag_dest(QUEUE_TARGETS, 
				gtk.gdk.ACTION_DEFAULT|gtk.gdk.ACTION_MOVE)
		#self.treeview.connect("drag-motion",self.check_contexts)
		#self.treeview.connect("drag-drop",self.dnd_handler)
		self.treeview.connect("drag-data-received",self.add_it)

	def check_contexts(self,treeview,context,selection,info,timestamp):
		context.drag_status(gtk.gdk.ACTION_COPY,timestamp)
		#print selection.get_text()
		return True

	def dnd_handler(self,treeview,context,selection,info,timestamp,b=None,c=None):
		'''
		'''
		tgt = treeview.drag_dest_find_target(context,[('text/plain',0,0),('GTK_TREE_MODEL_ROW',2,0)])
		#print treeview.drag_dest_get_target_list()
		data = treeview.drag_get_data(context,tgt)
		#print locals(),context.get_data(tgt)
		return True
	
	def add_it(self,treeview,context,x,y,selection,target,timestamp):
		#print locals()
		treeview.emit_stop_by_name("drag-data-received")
		#target = treeview.drag_dest_find_target(context,[("text/plain",0,0)])
		if timestamp !=0:
			text = self.parse_received_data(selection.get_text())
			text.reverse()
			while len(text) > 0:
				i = text.pop()
				if i[:7] == "file://":
					file = i[7:].replace("%20"," ")
				print file
				self.add(file)
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
		

