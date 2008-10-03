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
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @author    Maximiliano Valdez Gonzalez <garaged@gmail.com>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

import dbus, gobject
from dbus.mainloop.glib import DBusGMainLoop

class Pidgin():
	"""
	Class to set pidgin's message, tests if pidgin and its dbus is accesible, and puts the current song played on the message
	"""
	def __init__(self):
		self.obj = None
		self.SessionStart()

	def SetMessage(self,message):
		if ( self.obj is not None ):
			current = self.purple.PurpleSavedstatusGetType(self.purple.PurpleSavedstatusGetCurrent())
			status = self.purple.PurpleSavedstatusNew("", current)
			self.purple.PurpleSavedstatusSetMessage(status, message)
			self.purple.PurpleSavedstatusActivate(status)

	def SessionStart(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		session_bus = dbus.SessionBus()
		try:
			self.obj = session_bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
			self.purple = dbus.Interface(self.obj, "im.pidgin.purple.PurpleInterface")
		except:
			self.obj = None

pidgin_obj = Pidgin()
def set_message(message):
	"""
	Convenient helper function to try the DBus connection if it's not already opened
	Could be done inside the Pidgin.SetMessage() but I don't like the idea, this is more flexible
	"""
	if ( pidgin_obj.obj is None ):
		pidgin_obj.SessionStart()
	pidgin_obj.SetMessage(message)

if __name__ == "__main__":
	pass


