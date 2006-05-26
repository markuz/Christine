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



import gtk, os, gobject, gconf

class glade_xml:
	def __init__(self,file,root=None):
		'''constructor, receives the name of initialize gtk.glade.XML'''
		import gtk.glade
		#if os.path.isdir("./locale/"):
		#	locale_dir= "./locale"
		#else:
		#	locale_dir = "/usr/share/locale"
		#gtk.glade.bindtextdomain("gpkg",locale_dir)
		#gtk.glade.textdomain("gpkg")
		self.wdir = "./gui/"
		self.xml = gtk.glade.XML(os.path.join(self.wdir,file),root)
		self.get_widget = self.xml.get_widget

	def __getitem__(self,widget):
		'''
		returns the widget acording to the name of the widget
		'''
		return self.xml.get_widget(widget)
	def signal_autoconnect(self,signals):
		'''
		Signal autoconnect wrapper.
		'''
		self.xml.signal_autoconnect(signals)

class gtk_misc:
	def __init__(self):
		if os.path.isdir("./gui/pixmaps/"):
			self.wdir = "./gui/pixmaps/"
		else:
			self.wdir = "somwhere"

	def gen_pixbuf(self,imagefile):
		'''Create a pixbuf from  a file'''
		#try:
		pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.wdir,imagefile))
		return pixbuf
		#except:
		#	raise IOError,"There is no pixmap called %s"%imagefile
	
	def set_image(self,widget,filename):
		image = gtk.Image()
		image.set_from_pixbuf(self.gen_pixbuf(filename))
		widget.set_image(image)
		
	def image(self,filename):
		image = gtk.Image()
		image.set_from_pixbuf(self.gen_pixbuf(filename))
		image.show()
		return image

	def set_toolbutton_image(self,widget,filename):
		image = self.image(filename)
		widget.set_icon_widget(image)
	

class christine_gconf:
	def __init__(self):
		self.dir = "/apps/christine"
		self.bool_keys = {"ui/small_view":False,
						"ui/visualization":False,
						"control/shuffle":False,
						"control/repeat":False,
						"ui/show_artist":True,
						"ui/show_album":True,
						"ui/show_type":True}
		self.string_keys = {"backend/audiosink":"esdsink",
						"backend/videosink":"xvimagesink",
						"backend/video-aspect-ratio":"1/1",
						"backend/vis-plugin":"goom"}
		self.gconf = gconf.client_get_default()
		self.gconf.add_dir(self.dir,gconf.CLIENT_PRELOAD_RECURSIVE)
		self.set_initial_values()
	
		self.notify_add = self.gconf.notify_add
	
	def toggle_widget(self,client,cnx_id,entry,widget):
		widget.set_active(entry.get_value.get_bool())
	
	def toggle_visible(self,client,cnx_id,entry,widget):
		if entry.get_value.get_bool():
			widget.show()
		else:
			widget.hide()
		
	def toggle(self,widget,entry):
		self.gconf.set_value(entry,widget.get_active())
	
	def set_initial_values(self):
		if not self.get_bool("has_initial_keys"):
			self.set_value("has_initial_keys",True)
			for key in self.string_keys.keys():
				self.set_value(key,self.string_keys[key])
			for key in self.bool_keys.keys():
				self.set_value(key,self.bool_keys[key])
	
	def __getitem__(self,key,value):
		pass
	def get_bool(self,key):
		return self.gconf.get_bool(os.path.join(self.dir,key))

	def get_string(self,key):
		return self.gconf.get_string(os.path.join(self.dir,key))
	
	def get_int(self,key):
		return self.gconf.get_int(os.path.join(self.dir,key))
	
	def get_float(self,key):
		return self.gconf.get_float(os.path.join(self.dir,key))

	def set_value(self,key,value):
		t = type(value)
		print os.path.join(self.dir,key),value
		if t == type(1):
			self.gconf.set_int(os.path.join(self.dir,key),value)
		elif t == type(""):
			self.gconf.set_string(os.path.join(self.dir,key),value)
		elif t == type(True):
			self.gconf.set_bool(os.path.join(self.dir,key),value)
		elif t == type (1.0):
			self.gconf.set_float(os.path.join(self.dir,key),value)
		else:
			raise TypeError,"value is not int, bool or string"
	
class error:
	def __init__(self,text):
		xml = glade_xml("error.glade")
		dialog		= xml["dialog"]
		error_label = xml["error"]
		error_label.set_text(text)
		dialog.run()
		dialog.destroy()
