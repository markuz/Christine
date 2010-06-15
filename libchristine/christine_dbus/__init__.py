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
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

#
# This package includes all dbus related stuff for Christine Media Player.
#

from libchristine.pattern.Singleton import Singleton
from libchristine.ui import interface
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import os
import re
from libchristine.christineConf import christineConf
from libchristine.Events import christineEvents
from libchristine.gui.GtkMisc import GtkMisc
from libchristine.Logger import LoggerManager
from libchristine.ChristineCore import ChristineCore


main_loop = DBusGMainLoop()


DBUS_SESSION = dbus.SessionBus(mainloop = main_loop)
iface = interface()
iface.DBus_Session = DBUS_SESSION


DBUS_NAME = 'org.christine'
DBUS_PATH = '/org/christine'

class christineDBus(dbus.service.Object,GtkMisc):
	'''
	Class that serves as interface between christine stuff and dbus.
	'''
	def __init__(self):
		GtkMisc.__init__(self)
		self.core = ChristineCore()
		self.christineConf = christineConf()
		self.Events = christineEvents()
		self.__Logger = LoggerManager().getLogger('christineDBus')
		global DBUS_SESSION
		bus_name = dbus.service.BusName(DBUS_NAME, bus=DBUS_SESSION)
		dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
		self.christineConf.notifyAdd('backend/last_played', self.emit_last_played)
	
	@dbus.service.method(DBUS_NAME)
	def set_location(self, uri):
		res = self.core.Player.set_location(uri)
		return res
	@dbus.service.method(DBUS_NAME)
	def play(self):
		self.core.Player.playIt()
		return True
	
	@dbus.service.method(DBUS_NAME)
	def pause(self):
		self.core.Player.pause()
		return True
	
	@dbus.service.method(DBUS_NAME)
	def go_prev(self):
		iface.coreClass.goPrev()
		return True
	
	@dbus.service.method(DBUS_NAME)
	def go_next(self):
		iface.coreClass.goNext()
		return True
	# Library stuff
	
	@dbus.service.method(DBUS_NAME)
	def current_location(self):
		location = self.core.Player.get_location
		if not location:
			result = ''
		else:
			result = location
		return result
	
	@dbus.service.method(DBUS_NAME)
	def get_location(self):
		return self.core.Player.location
	
	@dbus.service.method(DBUS_NAME)
	def now_playing(self):
		return self.core.Player.getLocationlocation

	@dbus.service.method(DBUS_NAME)
	def get_tags(self, uri):
		'''
		Devuelve un diccionario con los tags del elemento definido por 
		uri
		@param uri:
		'''
		result = iface.db.getItemByPath(uri)
		return self.return_dict(result)
	
	def return_dict(self, result):
		ndict = {}
		for key, value in result.iteritems():
			ndict[u'%s'%key] = u'%s'%self.encode_text(str(value))
		return dbus.Dictionary(ndict, signature=dbus.Signature('sv'))
	
	@dbus.service.method(DBUS_NAME)
	def add_to_queue(self, uri):
		self.core.Queue.add(uri)
	
	@dbus.service.method(DBUS_NAME)
	def get_playlists(self):
		'''
		Return the playlists in the database
		'''
		result = iface.db.getPlaylists()
		return dbus.Array(result)
	
	def get_tracks_on_playlist(self, playlistname):
		'''
		Returns the tracks in the playlist
		@param playlistname:
		'''
		idlist = iface.db.PlaylistIDFromName(list)
		result = iface.db.getItemsForPlaylist(idlist)
		return self.return_dict(result)
		
	
	@dbus.service.method(DBUS_NAME)
	def get_radios(self):
		'''
		Return the radios in the database
		'''
		result = iface.db.getRadio()
		return dbus.Array(result)
	
	@dbus.service.method(DBUS_NAME)
	def exit(self):
		iface.coreClass.quitGtk()
	
	@dbus.service.method(DBUS_NAME)
	def put_in_queue(self, uri):
		iface.coreClass.Queue.add(uri)
		return True

	@dbus.service.method(DBUS_NAME)
	def decreaseVolume(self):
		"""
		Decrease the volume
		"""
		iface.coreClass.decreaseVolume()
	
	@dbus.service.method(DBUS_NAME)
	def increaseVolume(self):
		"""
		Increase the volume
		"""
		iface.coreClass.increaseVolume()

	@dbus.service.method(DBUS_NAME)
	def mute(self):
		"""
		Set mute
		"""
		iface.coreClass.mute()
		

	#Signals
	
	def emit_last_played(self, *args):
		file = self.christineConf.getString('backend/last_played')
		try:
			self.NewLocation(file)
		except:
			pass
	
	
	
	@dbus.service.signal(dbus_interface='org.christine', signature='s')
	def NewLocation(self, location):
		self.__Logger.info(location)
	
if __name__ == "__main__":
	a = christineDBus()
