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


#import gtk,gobject
from lib_christine.libs_christine import *
from lib_christine.gtk_misc import *
#from lib_christine.library import *
from lib_christine.trans import *


class preferences(gtk_misc):
	def __init__(self):
		gtk_misc.__init__(self)
		self.gconf = christine_gconf()
		self.xml = glade_xml("preferences.glade")
		self.xml.signal_autoconnect(self)
		self.audiosink = self.xml["audiosink"]
		self.audiosink.connect("changed",self.update_sink,"audiosink")
		self.videosink = self.xml["videosink"]
		self.videosink.connect("changed", self.update_sink,"videosink")
		self.fmodel = gtk.ListStore(str)
		self.ftreeview = self.xml["ftreeview"]
		self.ftreeview.set_model(self.fmodel)
		self.fadd = self.xml["fadd"]
		self.fdel = self.xml["fdel"]
		self.update_fmodel()
		self.__set_fcolumns()
		self.gconf.notify_add("/apps/christine/backend/allowed_files",lambda a,b,c,d:self.update_fmodel())
		self.select_sinks()
		dialog	 = self.xml["main_window"]
		dialog.set_icon(self.gen_pixbuf("logo.png"))
		self.set_checkboxes()
		dialog.run()
		dialog.destroy()

	def __set_fcolumns(self):
		render = gtk.CellRendererText()
		render.set_property("editable",True)
		render.connect("edited",self.on_cursor_changed)
		column = gtk.TreeViewColumn("Extension",render,text = 0)
		self.ftreeview.append_column(column)

	def __save_fmodel(self):
		 exts = ",".join([self.fmodel.get_value(k.iter,0) for k in self.fmodel])
		 self.gconf.set_value("backend/allowed_files",exts)

	def on_cursor_changed(self,render,path,value):
		iter = self.fmodel.get_iter(path)
		self.fmodel.set_value(iter,0,value)
		self.__save_fmodel()

	def update_fmodel(self):
		self.fmodel.clear()
		extensions = self.gconf.get_string("backend/allowed_files").split(",")
		extensions.sort()
		if len(extensions) < 1:
			return True
		while len(extensions) > 0:
			ext = extensions.pop()
			iter = self.fmodel.append()
			self.fmodel.set(iter,0,ext)


	def add_extension(self,widget):
		print "add_extension"
		iter = self.fmodel.append()
		self.fmodel.set(iter,0,translate("New extension"))
		self.__save_fmodel()
	
	def remove_extension(self,widget):
		selection = self.ftreeview.get_selection()
		model,iter = selection.get_selected()
		if iter != None:
			model.remove(iter)
			self.__save_fmodel()

	def select_sinks(self):
		videosink = self.gconf.get_string("backend/videosink")
		audiosink = self.gconf.get_string("backend/audiosink")
		audio_m = self.audiosink.get_model()
		video_m = self.videosink.get_model()
		a = 0
		for i in audio_m:
			if i[0] == audiosink:
				self.audiosink.set_active(a)
				break
			a += 1
		a = 0
		for i in video_m:
			if i[0] == videosink:
				self.videosink.set_active(a)
				break
			a += 1

	def update_sink(self,combobox,sink):
		path = combobox.get_active()
		model = combobox.get_model()
		selected = model.get_value(model.get_iter(path),0)
		self.gconf.set_value("backend/%s"%sink,selected)
	
	def set_checkboxes(self):
		self.artist = self.xml["artist"]
		self.artist.set_active(self.gconf.get_bool("ui/show_artist"))
		self.artist.connect("toggled",self.gconf.toggle,"ui/show_artist")

		self.album = self.xml["album"]
		self.album.set_active(self.gconf.get_bool("ui/show_album"))
		self.album.connect("toggled",self.gconf.toggle,"ui/show_album")

		self.type = self.xml["type"]
		self.type.set_active(self.gconf.get_bool("ui/show_type"))
		self.type.connect("toggled",self.gconf.toggle,"ui/show_type")

		self.length = self.xml["length"]
		self.length.set_active(self.gconf.get_bool("ui/show_length"))
		self.length.connect("toggled",self.gconf.toggle,"ui/show_length")
	
		self.track_number = self.xml["track_number"]
		self.track_number.set_active(self.gconf.get_bool("ui/show_tn"))
		self.track_number.connect("toggled",self.gconf.toggle,"ui/show_tn")
		
		self.play_count = self.xml["play_count"]
		self.play_count.set_active(self.gconf.get_bool("ui/show_play_count"))
		self.play_count.connect("toggled",self.gconf.toggle,"ui/show_play_count")

		self.genre = self.xml["genre"]
		self.genre.set_active(self.gconf.get_bool("ui/show_genre"))
		self.genre.connect("toggled",self.gconf.toggle,"ui/show_genre")


		self.notify_area = self.xml["notification_area"]
		self.notify_area.set_active(self.gconf.get_bool("ui/show_in_notification_area"))
		self.notify_area.connect("toggled",self.gconf.toggle,"ui/show_in_notification_area")

		self.libnotify = self.xml["pynotify"]
		self.libnotify.set_active(self.gconf.get_bool("ui/show_pynotify"))
		self.libnotify.connect("toggled",self.gconf.toggle,"ui/show_pynotify")

