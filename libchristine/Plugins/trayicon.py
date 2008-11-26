#! /usr/bin/env python
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

import gtk

from libchristine.christineConf import christineConf
from libchristine.Logger import LoggerManager
from libchristine.Share import Share
from libchristine.ui import interface
from libchristine.Plugins.plugin_base import plugin_base
from libchristine.Events import christineEvents

class trayicon(plugin_base):
	'''
	This class creates the tray icon for the christine media player.
	'''
	def __init__(self):
		plugin_base.__init__(self)
		self.name = 'TryIcon'
		self.description = 'This plugins shows a Try Icon on the notification area'
		self.christineConf   = christineConf()
		self.Events = christineEvents()
		if not self.christineConf.exists('trayicon/enabled'):
			self.christineConf.setValue('trayicon/enabled', True)
		self.christineConf.notifyAdd('trayicon/enabled', 
							lambda *args: self.__create_and_delete())
		self.__Share   = Share()
		self.__Logger = LoggerManager().getLogger('tryIcon')
		self.interface = interface()
		self.__IsHidden =  False
		self.__buildTrayIcon()
		self.Events.addWatcher('gotTags', self.gotTags)
		
		self.interface.TrayIcon = self
	
	def __create_and_delete(self, *args):
		if self.active:
			self.__buildTrayIcon()
		else:
			del self.TrayIcon
			#self.TrayIcon.destroy()
	
	def pause(self, *args):
		self.interface.coreClass.pause(*args)
	
	def goPrev(self, *args):
		self.interface.coreClass.goPrev(*args)
	
	def goNext(self,*args):
		self.interface.coreClass.goNext(*args)
	
	def __buildTrayIcon(self):
		"""
		Show the TrayIcon
		"""
		if self.active:
			self.TrayIcon = gtk.StatusIcon()
			self.TrayIcon.set_from_pixbuf(self.__Share.getImageFromPix('trayicon'))
			self.TrayIcon.connect('popup-menu', self.__trayIconHandlerEvent)
			self.TrayIcon.connect('activate',   self.__trayIconActivated)
			self.TrayIcon.set_tooltip('Christine Baby!')
			self.TrayIcon.set_visible(True)

	def __trayIconHandlerEvent(self, widget, event, time):
		"""
		TrayIcon handler events
		"""
		# If the event is a button press event and it was
		# the third button then show a popup menu
		if (event == 3):
			XML = self.__Share.getTemplate('MenuTrayIcon')
			XML.signal_autoconnect(self)

			popup = XML['menu']
			popup.popup(None, None, None, 3, gtk.get_current_event_time())
			popup.show_all()

	def __trayIconActivated(self, status):
		"""
		This hide and then show the window,
		intended when you want to show the window
		in your current workspace
		"""
		if (self.__IsHidden == True):
			self.interface.coreWindow.show()
		else:
			self.interface.coreWindow.hide()
		self.__IsHidden = not self.__IsHidden

	def trayIconPlay(self,widget = None):
		self.interface.playButton.set_active(True)
	
	def gotTags(self, tags):
		if self.active:
			tooltext = "%s\n" % tags['title']
			if tags['artist']:
				tooltext += "by %s\n" % tags['artist']
			if tags['album']:
				tooltext += " from %s " % tags['album']
			self.TrayIcon.set_tooltip(tooltext)	
			

	def get_active(self):
		return self.christineConf.getBool('trayicon/enabled')
	
	def set_active(self, value):
		return self.christineConf.setValue('trayicon/enabled', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')
