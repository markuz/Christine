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

import gtk

from libchristine.christineConf import christineConf
from libchristine.Logger import LoggerManager
from libchristine.Share import Share
from libchristine.ui import interface

class tryIcon:
	'''
	This class creates the tray icon for the christine media player.
	'''
	def __init__(self):
		self.__Share   = Share()
		self.__Logger = LoggerManager().getLogger('tryIcon')
		self.interface = interface()
		self.__IsHidden =  False
		print self.interface
		self.__christineGconf   = christineConf()
		self.__buildTrayIcon()
		self.pause = self.interface.coreClass.pause
		self.goPrev = self.interface.coreClass.goPrev
		self.goNext = self.interface.coreClass.goNext
		self.interface.TrayIcon = self

	def __buildTrayIcon(self):
		"""
		Show the TrayIcon
		"""
		self.TrayIcon = gtk.StatusIcon()
		self.TrayIcon.set_from_pixbuf(self.__Share.getImageFromPix('trayicon'))
		self.TrayIcon.connect('popup-menu', self.__trayIconHandlerEvent)
		self.TrayIcon.connect('activate',   self.__trayIconActivated)
		self.TrayIcon.set_tooltip('Christine Baby!')
		value = self.__christineGconf.getBool('ui/show_in_notification_area')
		self.TrayIcon.set_visible(value)

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
