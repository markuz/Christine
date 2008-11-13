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
from libchristine.Plugins.plugin_base import plugin_base
from libchristine.globalvars import PROGRAMNAME
from libchristine.Events import christineEvents

try:
	import pynotify
	pynotify.Urgency(pynotify.URGENCY_NORMAL)
	pynotify.init(PROGRAMNAME)
	version = pynotify.get_server_info()['version'].split('.')
	if (version < [0, 3, 6]):
		raise ImportError("server version is %d.%d.%d, 0.3.6 or major required" % version)

	PYNOTIFY = True
except ImportError:
	print 'no pynotify available'
	PYNOTIFY = False

class christinePyNotify(plugin_base):
	'''
	This plugins shows notify bubbles using python-notify
	'''
	def __init__(self):
		plugin_base.__init__(self)
		self.name = 'PyNotify'
		self.description = 'Shows notify bubbles'
		self.christineConf   = christineConf()
		self.Events = christineEvents()
		print self.Events
		if not self.christineConf.exists('pynotify/enabled'):
			self.christineConf.setValue('pynotify/enabled', True)
		self.__Share   = Share()
		self.__Logger = LoggerManager().getLogger('PyNotify')
		self.interface = interface()
		self.Events.addWatcher('gotTags', self.gotTags)
		
		self.interface.PyNotify = self
	
	def gotTags(self, tags):
		if PYNOTIFY and self.active:
			notify_text = "<big>%s</big>\n" % tags['title']
			if tags['artist']:
				notify_text += " by <big>%s</big>\n" % tags['artist']
			if tags['album']:
				notify_text += " from <big>%s</big>" % tags['album']
				
			if getattr(self, 'Notify', False):
				self.Notify.close()
			pixmap = self.__Share.getImage('trayicon')
			self.Notify = pynotify.Notification('christine', '',pixmap)
			if getattr(self.interface, 'TrayIcon', False):
				self.Notify.attach_to_status_icon(self.interface.TrayIcon.TrayIcon)
			self.Notify.set_property('body', notify_text)
			self.Notify.show()

	def get_active(self):
		return self.christineConf.getBool('pynotify/enabled')
	
	def set_active(self, value):
		return self.christineConf.setValue('pynotify/enabled', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')