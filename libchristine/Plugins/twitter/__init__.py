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
# @author    Maximiliano Valdez Gonzalez <garaged@gmail.com>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import thread


#
# This is just a hack... And if we plan to use it as a plugin should be
# Bigger and Stronger!
#

import os
from libchristine.ui import interface
from libchristine.Tagger import Tagger
from libchristine.Share import Share
from libchristine.Plugins.plugin_base import plugin_base, christineConf
from libchristine.ChristineCore import ChristineCore
import urllib2
from urllib import urlencode

__name__ = _('Twitter')
__description__  = _('This plugins send and update to your twitter account')
__author__  = ['Marco Antonio Islas Cruz <markuz@islascruz.org>']
__enabled__ = christineConf.getBool('twitter/enabled')


class twitter(plugin_base):
	"""
	Class to update twitter with the song being played on Christine
	"""
	def __init__(self):
		plugin_base.__init__(self)
		self.name = __name__
		self.description = __description__
		#self.christineConf.notifyAdd('backend/last_played', self.postMessage)
		self.christineConf.notifyAdd('twitter/enabled', self.postMessage)
		self.core = ChristineCore()
		self.core.Player.connect('end-of-stream', self.postMessage)
		self.tagger = Tagger()
		self.Share = Share()
		self.interface = interface()
		self.logger = self.interface.LoggerManager.getLogger('PluginTwitter')

	def postMessage(self, args):
		if not self.active:
			return
		file = self.christineConf.getString('backend/last_played')
		username = self.christineConf.getString('twitter/username')
		if not username:
			self.christineConf.setValue('twitter/username','user@somemail.com')
		password = self.christineConf.getString('twitter/password')
		if not password:
			self.christineConf.setValue('twitter/password','1234567890')
		msg = self.christineConf.getString('twitter/message')
		if not msg:
			self.christineConf.setValue('twitter/message',' [christine] _title_ by _artist_ from _album_')
		msg = self.tagger.taggify(file, msg)
		url = "http://twitter.com/statuses/update.xml"
		thread.start_new(self.httpConn, (url, msg, username, password))

	def httpConn(self,url, msg, username, password):
		"""
		Makes authenticated http connection, to avoid shell opening with curl
		This could be on another module... coded smartly
		"""
		pwd_mngr = urllib2.HTTPBasicAuthHandler()
		pwd_mngr.add_password("Twitter API", url, username, password)
		opener = urllib2.build_opener(pwd_mngr)
		urllib2.install_opener(opener)
		try:
			urllib2.urlopen(url,urlencode({"status": msg}))
		except urllib2.HTTPError, e :
			if e.code == 401:
				self.logger.info(_('not authorized'))
			elif e.code == 404:
				self.logger.info(_('not found'))
			elif e.code == 503:
				self.logger.info(_('service not available'))
			else:
				self.logger.info(_('unknown error'))
		else:
			self.logger.info(_('twitt -> %s'%msg))

	def get_active(self):
		return self.christineConf.getBool('twitter/enabled')

	def set_active(self, value):
		__enabled__ = value
		return self.christineConf.setValue('twitter/enabled', value)
	
	def configure(self):
		'''
		Configure twitter plugin 
		'''
		xml = self.Share.getTemplate('twitter')
		dialog = xml['dialog']
		username = xml['username']
		password = xml['password']
		message = xml['message']
		username.set_text(self.christineConf.getString('twitter/username'))
		password.set_text(self.christineConf.getString('twitter/password'))
		password.set_visibility(False)
		message.set_text(self.christineConf.getString('twitter/message'))
		username.connect('changed', self.__change_value, 'username')
		password.connect('changed', self.__change_value, 'password')
		password.connect('focus-in-event', lambda widget, event: widget.set_visibility(True))
		password.connect('focus-out-event', lambda widget, event: widget.set_visibility(False))
		message.connect('changed', self.__change_value, 'message')
		dialog.run()
		dialog.destroy()
	
	def __change_value(self, entry, key):
		'''
		Change a value in the twitter section
		@param entry: gtk.Entry that emits "changed" signal
		@param key: key of the section (username, password, message)
		'''
		nkey = 'twitter/%s'%key
		self.christineConf.setValue(nkey, entry.get_text())
		
		
		
		

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')
