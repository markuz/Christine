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


from lib_christine.discoverer import *
from lib_christine.gtk_misc import *
from lib_christine.library import *

class Handler(gtk_misc):
	def __init__(self,interface):
		self.interface = interface
		self.discoverer = discoverer()
		self.discoverer.bus.add_watch(self.message_handler)
		gtk_misc.__init__(self)
		self.gconf = christine_gconf()
		active = self.gconf.gconf.key_is_writable("/apps/christine/plugins/show_properties")
		if active == None:
			self.gconf.set_value("plugins/show_properties",True)
		self.values = {
				"name":"Show Properties",
				"active":True,
				"Author": "Marco Antonio Islas Cruz",
				"ref":self
				}
		menuitem = gtk.MenuItem("properties1")
		menuitem.show()
		menuitem.connect("activate",self.show)
		self.interface.menus["edit"].append(menuitem)
	
	def start(self):
		pass

	def show(self,widget):
		selection = self.interface.library_treeview.get_selection()
		model,iter = selection.get_selected()
		file = model.get_value(iter,PATH)
		self.discoverer.set_location(file)
		xml				= glade_xml("properties.glade")
		self.dialog			= xml["dialog"]
		self.file		= xml["file"]
		#self.file.set_text(file)
		self.title		= xml["title"]
		self.tn			= xml["tn"]
		self.album		= xml["album"]
		self.artist		= xml["artist"]
		self.genre		= xml["genre"]
		self.date		= xml["date"]
		self.acodec		= xml["acodec"]
		self.vcodec		= xml["vcodec"]
		self.mode		= xml["mode"]
		self.bitrate	= xml["bitrate"]
		self.dialog.run()
		self.dialog.destroy()
		
	def message_handler(self,a,b):
		if b.type == gst.MESSAGE_TAG:
			self.discoverer.found_tags_cb(b.parse_tag())
			self.check_tags()
		return True
			
	def check_tags(self):
		date = self.discoverer.get_tag("date")
		if type(date) == gst.Date:
			day = date.day
			month = date.month
			year = date.year
		else:
			day,month,year = (0,0,0)
		self.tn.set_text(str(self.discoverer.get_tag("track-number")))
		self.title.set_text(self.discoverer.get_tag("title"))
		self.album.set_text(self.discoverer.get_tag("album"))
		self.artist.set_text(self.discoverer.get_tag("artist"))
		self.genre.set_text(self.discoverer.get_tag("genre"))
		self.date.set_text("%d-%d-%d"%(year,month,day))
		self.acodec.set_text(self.discoverer.get_tag("audio-codec"))
		self.vcodec.set_text(self.discoverer.get_tag("video-codec"))
		self.mode.set_text(self.discoverer.get_tag("mode"))
		self.bitrate.set_text(str(self.discoverer.get_tag("bitrate")))
