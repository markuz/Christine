#! /usr/bin/env python
# -*- coding: latin-1 -*-

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


from libchristine.GtkMisc import *
from libchristine.Share import Share
import ConfigParser

(LIST_NAME,
LIST_TYPE,
LIST_PIXBUF) = xrange(3)

class sources_list (GtkMisc):
	def __init__(self):
		GtkMisc.__init__(self)
		self.__Share = Share()
		self.xml = self.__Share.getTemplate('TreeViewSources','treeview')
		self.__gen_model()
		self.treeview = self.xml["treeview"]
		self.treeview.set_headers_visible(True)
		self.treeview.set_model(self.model)
		self.__append_columns()
	
	def __gen_model(self):
		self.model = gtk.ListStore(str,str,gtk.gdk.Pixbuf)
		p = os.path.join(os.environ["HOME"],".christine","sources")
		files = os.listdir(p)
		for fname in files:
			file = os.path.join(os.environ["HOME"],".christine","sources",fname)
			if os.path.isfile(os.path.join(file)):
				icon = 'logo'
				fname = os.path.split(file)[-1]
				ltype = '1'
				pixbuf = self.__Share.getImageFromPix(icon)
				pixbuf = pixbuf.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
				iter = self.model.append()
				self.model.set(iter,LIST_NAME,fname,
						LIST_TYPE,ltype,
						LIST_PIXBUF,pixbuf)

	def __append_columns(self):
		column = gtk.TreeViewColumn("Source")
		text = gtk.CellRendererText()
		pix= gtk.CellRendererPixbuf()
		column.pack_start(pix,False)
		column.pack_start(text,True)
		column.add_attribute(text,"text",LIST_NAME)
		column.add_attribute(pix,"pixbuf",LIST_PIXBUF)
		self.treeview.append_column(column)
	
	
		

		




	
