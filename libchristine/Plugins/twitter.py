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
# @author    Marco Antonio Islas Cruz
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt


#
# This is just a hack... And if we plan to use it as a plugin should be 
# Bigger and Stronger!
#

import os
from libchristine.ui import interface
from libchristine.christineConf import christineConf
from libchristine.Tagger import Tagger

class twitter:
	"""
	Class to set pidgin's message, tests if pidgin and its dbus is accesible, and puts the current song played on the message
	"""
	def __init__(self):
		self.interface = interface()
		self.christineConf = christineConf()
		self.christineConf.notifyAdd('backend/last_played', self.postMessage)
		self.christineConf.notifyAdd('twitter/enabled', self.postMessage)
		self.tagger = Tagger()
		self.__switch_enabled()
	
	def __switch_enabled(self, *args):
		self.enabled =  self.christineConf.getBool('twitter/enabled')
	

	def postMessage(self, args):
		if not self.enabled:
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
		tags =  self.tagger.readTags(file)
		print '>>', msg
		for i in tags.keys():
			msg = msg.replace('_%s_'%i, str(tags[i]))
		print '>>', msg
		tweetcmd = '''curl -u %s:%s -d status="%s" http://twitter.com/statuses/update.xml 
		'''%(username, password, msg)
		os.popen4(tweetcmd)
