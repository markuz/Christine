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
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
from ConfigParser import ConfigParser
from libchristine.pattern.Singleton import Singleton
from libchristine.Translator import *
from libchristine.Logger import LoggerManager
import gtk
import sys
import os



class christineConf(Singleton):
	'''
	This is the christine replace for the gconf module. Basicly it does what
	gconf do but in a more convenient way for christine, and stripping all
	the things that gconf has.

	This implies that using christine with this module, all config in
	the gconf module no longer work, you must use the config file stored
	in ~/.christine.conf

	The christine.conf file is a simple .ini file wich is handled by christine
	using the configParser module.

	This module serves as proxy to the configParser module, and it will know
	when any value is changed, then, __notify to any watcher.
	'''
	def __init__(self):
		'''
		Constructor
		'''
		self.filepath = os.path.join(os.environ['HOME'],'.christine','christine.conf')
		self.configParser = ConfigParser()
		self.__notify = {}
		if os.path.exists(self.filepath):
			if not os.path.isfile(self.filepath):
				msg = translate('%s is not a file'%self.filepath)
				sys.stderr.write(msg)
			f = open(self.filepath)
			self.configParser.readfp(f)
			f.close()
		else:
			self.create_basic_config_file()

	def create_basic_config_file(self):
		f = open(self.filepath, 'w')
		if not self.configParser.has_section('ui'):
			self.configParser.add_section('ui')
		self.configParser.set('ui','show_artist',"true")
		self.configParser.set('ui','show_album',"true")
		self.configParser.set('ui','show_play_count',"true")
		self.configParser.set('ui','show_tn',"true")
		self.configParser.set('ui','show_length',"true")
		self.configParser.set('ui','show_genre',"true")
		self.configParser.set('ui','show_in_notification_area',"true")
		self.configParser.set('ui','show_pynotify',"true")
		self.configParser.set('ui','show_type',"true")
		self.configParser.set('ui','small_view',"false")
		self.configParser.set('ui','visualization',"false")
		self.configParser.set('ui','LastFolder',os.environ['HOME'])
		if not self.configParser.has_section('control'):
			self.configParser.add_section('control')
		self.configParser.set('control','shuffle',"true")
		self.configParser.set('control','repeat',"false")
		self.configParser.set('control','volume','0.8')
		if not self.configParser.has_section('backend'):
			self.configParser.add_section('backend')
		self.configParser.set('backend','audiosink','autoaudiosink')
		self.configParser.set('backend','videosink','ximagesink')
		self.configParser.set('backend','video-aspect-ratio','1/1')
		self.configParser.set('backend','aspect-ratio','1/1')
		self.configParser.set('backend','allowed_files','mp3,ogg,avi,wmv,mpg,mpeg,mpe,wav')
		self.configParser.set('backend','vis-plugin','goom')
		self.configParser.set('backend','last_played','')
		self.configParser.set('pidgin','message',"Escuchando: _artist_ - _title_ - en Christine")
		self.configParser.write(f)
		f.close()
		f = open(self.filepath, 'r')
		self.configParser.read(f)
		f.close()
		del f
		return True

	def resetDefaults(self):
		'''
		reset to defaults. behaviour is the same that using
		create_basic_config_file
		'''
		return self.create_basic_config_file()

	def toggleWidget(self, value, widget):
		'''
		Inverts the 'active' property in the widget using the value of the
		entry
		@param entry: connection entry
		@param widget: widget to work on
		'''
		widget.set_active(value)

	def toggleVisible(self, value, widget):
		'''
		Toggles the 'visible' property in the widget using the value of the
		entry
		@param entry: the conection entry
		@param widget: widget to work on
		'''
		if not isinstance(widget, gtk.TreeViewColumn):
			if value:
				widget.show()
			else:
				widget.hide()
		elif isinstance(widget, gtk.TreeViewColumn):
			widget.set_visible(value)
		else:
			raise TypeError('How should I show/hide this widget: ', widget)

	def toggle(self, widget, entry):
		'''
		Toggle the entry value according to widget
		@param widget:
		@param entry:
		'''
		self.setValue(entry, widget.get_active())

	def get(self, key, method = None):
		'''
		Returns the value of a key
		@param key: Key to work on
		'''
		vals = key.split('/')
		if len(vals) != 2:
			raise KeyError('The given key is not valid')
			return False
		section, option = vals
		if method == None:
			method = self.configParser.get
		try:
			result = method(section, option)
		except Exception, e:
			result = None
		return result


	def getBool(self, key):
		'''
		A convenience method which coerces the option in the specified
		section to a boolean value.
		@param key: key to work on
		'''
		val = self.get(key, self.configParser.getboolean)
		if val: return val
		else: return False

	def getString(self, key):
		'''
		A convenience method which coerces the option in the specified
		section to a string value.
		@param key: key to work on
		'''
		val = self.get(key)
		if val: return val
		else: return False

	def getInt(self, key):
		'''
		A convenience method which coerces the option in the specified
		section to a integet number.
		@param key: key to work on
		'''
		val = self.get(key, self.configParser.getint)
		if val: return val
		else: return 0

	def getFloat(self, key):
		'''
		A convenience method which coerces the option in the specified
		section to a floating point number.
		@param key: key to work on
		'''
		val = self.get(key, self.configParser.getfloat)
		if val: return val
		else: return 0.0

	def setValue(self, key, value):
		'''
		Set the value on the key.

		@param key: key to work on, must be in the section/option way
		@param value: value for the key
		'''
		vals = key.split('/')
		if len(vals) != 2:
			raise KeyError('The given key is not valid')
		section, option = vals
		if self.configParser.has_section(section):
			if not isinstance(value, str):
				nvalue = str(value).lower()
			else:
				nvalue = value
			oldvalue = self.getString(key)
			if oldvalue == nvalue:
				return True
			self.configParser.set(section, option, nvalue)
		else:
			self.configParser.add_section(section)
			self.configParser.set(section, option, value)
		f = open(self.filepath,'w')
		self.configParser.write(f)
		f.close()
		del f
		self.__executeNotify(key, value)

	def __executeNotify(self, key, value):
		if not self.__notify.has_key(key):
			return False
		for i in self.__notify[key]:
			func = i[0]
			args = i[1]
			func(value, *args)

	def notifyAdd(self, key, func, *args):
		'''
		Save the func reference in the __notify list to be run every time the
		value of the key changes.

		func(value, userdata..)

		@param key: key to be used
		@param func: func to execute
		@param *args: user data
		'''
		if not self.__notify.has_key(key):
			self.__notify[key] = []
		self.__notify[key].append((func, args))

	def notify_add(self, key, func, *args):
		'''
		the same has notifyAdd
		@param key:
		@param func:
		'''
		self.notifyAdd(self, key, func, *args)







