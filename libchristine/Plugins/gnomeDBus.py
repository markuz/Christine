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
# This module includes GNOME Media keys integration
#

from libchristine.christine_dbus import DBUS_SESSION
from libchristine.pattern.Singleton import Singleton
from libchristine.ui import interface
from libchristine.Plugins.plugin_base import plugin_base
from libchristine.gui.christineNotify import notifyWindow

import gobject
import os
import re

#determine gnome version  
#thanks to jean-luc coulon for his multilocale fix  
major = 2  
minor = 18 #default to 2.18 if there are problems in the following code  
output = os.popen("LANG=C gnome-about --gnome-version")  
pattern = re.compile(r'^Version: ([0-9]+)\.([0-9]+)\..*')  
for line in output.readlines():
	if pattern.match(line):
		major = pattern.search(line).group(1)
		minor = pattern.search(line).group(2)

class gnomeDBus(plugin_base):
	def __init__(self):
		'''
		Constructor
		'''
		plugin_base.__init__(self)
		self.name = 'GNOME Media Keys'
		self.description = 'Allows christine to react to GNOME media key press events'
		self.iface = interface()
		if (int(major) == 2) & (int(minor) > 20):
			self.obj = DBUS_SESSION.get_object('org.gnome.SettingsDaemon',
											'/org/gnome/SettingsDaemon/MediaKeys') 
			self.obj.connect_to_signal("MediaPlayerKeyPressed", self.mediak_press, 
						dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
		else:
			self.obj = DBUS_SESSION.get_object('org.gnome.SettingsDaemon',
											'/org/gnome/SettingsDaemon') 
			self.obj.connect_to_signal("MediaPlayerKeyPressed", self.mediak_press, 
						dbus_interface='org.gnome.SettingsDaemon')

	def mediak_press(self, *keys):
		'''
		This method is called everytime the MediaPlayerKeyPressed signal
		is emited by the org.gnome.SetingsDaemon object.
		'''
		for key in keys:
			if key == 'Play':
				state =  not self.iface.coreClass.PlayButton.get_active()
				self.iface.coreClass.PlayButton.set_active( state)
			elif key in ('Pause', 'Stop'):
				self.iface.coreClass.pause()
			elif key == 'Next':
				self.iface.coreClass.goNext()
			elif key == 'Previous':
				self.iface.coreClass.goPrev()
		a = notifyWindow()
		a.set_text(key)
			
