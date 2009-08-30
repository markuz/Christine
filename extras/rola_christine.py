#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2009 Marco Antonio Islas Cruz
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
# @copyright 2006-2009 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
 
version = "1.0"
 
__module_name__ = "rola_christine.py"
__module_version__ = version
__module_description = 'Shows the track in christine (requires christine from SVN)'
 
import dbus
import xchat
from dbus.mainloop.glib import DBusGMainLoop
 
class RolaChristine:
	def __init__(self):
		self.mainloop = DBusGMainLoop()
		self.dbus_session = dbus.SessionBus(mainloop = self.mainloop)
		xchat.prnt("rola-christine.py Version %s loaded!" %version)
		xchat.prnt("/rola-christine")
	
	def rola(self,word,word_eol,userdata):
		try:
			christine = self.dbus_session.get_object('org.christine', '/org/christine')
		except:
			xchat.command('Nada a mostrar.. :-(')
			return xchat.EAT_XCHAT
		uri = christine.now_playing()
		print uri
		tags = christine.get_tags(uri)
		title = '%s'%tags.get('title','')
		if not title:
			xchat.command('Nada a mostrar.. :-(')
			return xchat.EAT_XCHAT
		artist = "%s"%tags.get('artist','')
		if artist:
			artist = "%s -"%artist
		xchat.command("me esta escuchando: %s %s" %(artist,title))
		return xchat.EAT_XCHAT

control = RolaChristine()
xchat.hook_command("rola-christine",control.rola)
