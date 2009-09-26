#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2007 Marco Antonio Islas Cruz
#
# Christine is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Christine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @category  Multimedia
# @package   Christine
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

from libchristine.gui.GtkMisc import GtkMisc, glade_xml, error
from libchristine.Translator import translate
from libchristine.Share import Share
from libchristine.christineConf import christineConf
from libchristine.ui import interface
import gtk


class openRemote(GtkMisc):
	def __init__(self):
		'''
		Shows a dialog that let the user open a remote location.
		'''
		self.__Share = Share()
		self.__christineConf = christineConf()
		self.interface = interface()
		XML    = self.__Share.getTemplate('openRemote')
		comboboxentry  = XML['comboboxentry']
		entry = comboboxentry.get_child()
		self.dialog = XML['dialog']
		button  = XML['okbutton']
		entry.connect("key-press-event", self.__oRButtonClick,button)
		comboboxentry.connect("changed",self.__orChanged)
		self.dialog.set_icon(self.__Share.getImageFromPix('logo'))
		model = gtk.ListStore(str)
		comboboxentry.set_model(model)
		comboboxentry.set_text_column(0)
		stream_history = self.__christineConf.getString('backend/last_stream_played')
		self.stream_history = []
		if stream_history  and isinstance(stream_history,str):
			self.stream_history = stream_history.split(",")
			del stream_history
		for stream in self.stream_history:
			model.append([stream])
		if len(model):
			comboboxentry.set_active(0)
		response = self.dialog.run()
		if (response == gtk.RESPONSE_OK):
			self.open_remote(comboboxentry.get_child(), '')
		self.dialog.destroy()
		
	def open_remote(self, entry, location):
		location = entry.get_text()
		if not location:
			return False
		if location in self.stream_history:
			del self.stream_history[self.stream_history.index(location)]
			self.stream_history.append(location)
		else:
			if len(self.stream_history) < 10:
				self.stream_history.append(location)
			else:
				del self.stream_history[0]
				self.stream_history.append(location)
		stream_history=",".join([stream for stream in self.stream_history])
		self.__christineConf.setValue('backend/last_stream_played',stream_history)
		extension = location.split(".").pop()
		urldesc = None
		file = None
		if location.split(":")[0] == "file":
			file = ":".join(location.split(":")[1:])[2:]
		elif location[0] == '/':
			file = location
		if  file:
			try:
				urldesc = open(file)
			except IOError:
				error(translate('%s does not exists'%file))
				self.dialog.destroy()
				return False
		#Trye to get it on the net
		if not urldesc:
			import urllib
			gate = urllib.FancyURLopener()
			urldesc = gate.open(location)

		if extension == "pls":
			for i in urldesc.readlines():
				if i.lower().find("file") >= 0:
					location = i.split("=").pop().strip()
					break
			self.interface.coreClass.setLocation(location)
			self.interface.coreClass.simplePlay()
		elif extension == "m3u":
			lines = urldesc.readlines()
			if lines[0].lower() != "#extm3u":
				self.goNext()
			sites = []
			for i in range(len(lines)):
				if lines[i].split(":")[0].lower() == "#extinf":
					sites.append(lines[i+1])
			for i in sites:
				i = i.strip("\r\n").strip()
				self.interface.Queue.add(i)
			self.goNext()
		urldesc.close()

	def __orChanged(self,widget):
		'''
		Listen for items selected in the combobox
		'''
		model = widget.get_model()
		index = widget.get_active()
		entry = widget.get_child()
		if index > -1:
			selected = model[index][0]
			if selected and type(selected) == str:
				entry.set_text(selected)

	def __oRButtonClick(self,widget,event,button):
		'''
		Clicks the okbutton on ENTER key pressed
		'''
		if not widget.get_text():
			return False
		if event.keyval in (gtk.gdk.keyval_from_name('Return'),
				gtk.gdk.keyval_from_name('KP_Enter')):
			button.clicked()
		
		
