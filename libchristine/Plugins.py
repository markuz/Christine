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

import os,sys
from libchristine.Translator import *
from libchristine.GtkMisc import *
from libchristine.Share import *
import libchristine.ChristineDefinitions as ChristineDefinitions

sys.path.append(ChristineDefinitions.USERDIR)
if (not "--devel" in sys.argv):
	sys.path.append(ChristineDefinitions.SHARE_PATH)
import uplugins
import cplugins

def importName(modulename,name):
	try: 
		module = __import__(modulename,globals(),locals(),[name])
	except ImportError:
		return None
	return vars(module)[name]

class interface:
	pass

class ChristinePlugins(GtkMisc):
	def __init__(self,main):
		GtkMisc.__init__(self)
		self.main = main
		self.plugins = {}
		self.menuitems = {}
		self.__create_interface()
		files = os.listdir(os.path.join(os.environ["HOME"],
			".christine","uplugins"))
		files = [".".join(k.split(".")[:-1]) for k in files if k.split(".")[-1] == "py" and ".".join(k.split(".")[:-1]) != "__init__"]
		self.__imports(files,"uplugins")
		files = os.listdir(os.path.join(ChristineDefinitions.SHARE_PATH,"cplugins"))
		files = [".".join(k.split(".")[:-1]) for k in files if k.split(".")[-1] == "py" and ".".join(k.split(".")[:-1]) != "__init__"]
		self.__imports(files,"cplugins")

	
	def __create_interface(self):
		self.interface = interface
		self.interface.datadir = ChristineDefinitions.SHARE_PATH
		self.interface.list_vbox = self.main.VBoxList
		self.interface.menubar = self.main.MenuBar
		self.interface.search_box = self.main.EntrySearch
		#self.interface.list_box = self.main.list_box
		self.interface.list_vbox = self.main.VBoxList
		self.interface.library_treeview = self.main.TreeView
		self.interface.menus = self.main.Menus
		self.interface.pack = self.pack
		self.interface.register_on_menu = self.register_on_menu
		pass
	
	def pack(self,widget,item,start=False,expand=False,fill=False,border=0):
		element = getattr(self.interface,item)
		if start:
			pack = element.pack_start
		else:
			pack = element.pack_end
		pack(widget,expand,fill,border)
	
	def	register_on_menu(self, menuname, widget):
		self.menuitems[menuname] = widget

	def populate_menu(self,menu,menuname):
		keys = self.menuitems.keys()
		keys.sort()
		for i in keys:
			self.menuitems[i].unparent()
			menu.append(self.menuitems[i])
	

	def __imports(self,plugins,package):
		for i in plugins:
			module = importName(package,i)
			if module != None:
				a = module.Handler(self.interface)
				name = a.values["name"]
				self.plugins[name] = a.values
				if a.values["active"]:
					a.start()
