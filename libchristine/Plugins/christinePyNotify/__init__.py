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

from libchristine.Logger import LoggerManager
from libchristine.Share import Share
from libchristine.ui import interface
from libchristine.Plugins.plugin_base import plugin_base, christineConf
from libchristine.globalvars import PROGRAMNAME
from libchristine.Events import christineEvents
from libchristine.Translator import translate

logger = LoggerManager().getLogger('PyNotify')

try:
	import pynotify
	pynotify.Urgency(pynotify.URGENCY_NORMAL)
	pynotify.init(PROGRAMNAME)
	version = pynotify.get_server_info()['version'].split('.')
	if (version < [0, 3, 6]):
		msg = translate("server version is %d.%d.%d, 0.3.6 or major required" % version)
		raise ImportError(msg)
	PYNOTIFY = True
except ImportError,e:
	logger.info(translate('no pynotify available'))
	logger.exception(e)
	PYNOTIFY = False

__name__ = _('PyNotify')
__description__  = _('Shows notify bubbles')
__author__  = 'Marco Antonio Islas Cruz <markuz@islascruz.org>'
__enabled__ = christineConf.getBool('pynotify/enabled')


def _christinePyNotify(*args):
	result = pynotify.Notification(*args)
	return result


class christinePyNotify(plugin_base):
	'''
	This plugins shows notify bubbles using python-notify
	'''
	def __init__(self):
		plugin_base.__init__(self)
		self.name = __name__ 
		self.description = __description__
		self.Events = christineEvents()
		if not self.christineConf.exists('pynotify/enabled'):
			self.christineConf.setValue('pynotify/enabled', True)
		self.__Share   = Share()
		self.__Logger = LoggerManager().getLogger('PyNotify')
		self.interface = interface()
		self.Events.addWatcher('gotTags', self.gotTags)
		self.__Logger = logger
		self.interface.PyNotify = self
	
	def gotTags(self, tags):
		if PYNOTIFY and self.active:
			for k,v in tags.iteritems():
				if isinstance(v, str):
					tags[k] = self.encode_text(v)
			notify_text = "<big>%s</big>\n" % tags['title']
			if tags['artist']:
				notify_text += " by <big>%s</big>\n" % tags['artist']
			if tags['album']:
				notify_text += " from <big>%s</big>" % tags['album']
				
			if not getattr(self, 'Notify', False):
				pixmap = self.__Share.getImage('logo')
				self.Notify = _christinePyNotify('christine', '',pixmap)
			if getattr(self.interface, 'TrayIcon', False):
				self.Notify.attach_to_status_icon(self.interface.TrayIcon.TrayIcon)
			self.Notify.set_property('body', notify_text)
			self.Notify.show()

	def get_active(self):
		return self.christineConf.getBool('pynotify/enabled')
	
	def set_active(self, value):
		__enabled__ = value 
		return self.christineConf.setValue('pynotify/enabled', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')