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


from lib_christine.gtk_misc import *

(LIST_NAME,) = xrange(1)

class sources_list (gtk_misc):
	def __init__(self):
		gtk_misc.__init__(self)
		self.xml = glade_xml("sources_treeview.glade","treeview")
		self.__gen_model()
		self.treeview = self.xml["treeview"]
		self.treeview.set_model(self.model)
		self.__append_columns()
	
	def __gen_model(self):
		self.model = gtk.ListStore(str)
		p = os.path.join(os.environ["HOME"],".christine","sources")
		files = os.listdir(p)
		print files,len(files)
		while True:
			if len(files) == 0:
				print "lista vacia"
				break # Exit loop if there is nothing in the list.
			fname = files.pop()
			if os.path.isfile(os.path.join(os.environ["HOME"],".christine","sources",fname)):
				iter = self.model.append()
				self.model.set(iter,LIST_NAME,fname)
			else:
				print "no es archivo!!",fname

	def __append_columns(self):
		render = gtk.CellRendererText()
		source = gtk.TreeViewColumn("Source",render,text=LIST_NAME)
		source.set_visible(True)
		self.treeview.append_column(source)
