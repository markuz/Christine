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
# @category  GnomeConf
# @package   ChristineGConf
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import gconf
import gtk
from libchristine.Validator import *
from libchristine.pattern.Singleton import Singleton
from libchristine.Logger import ChristineLogger

#
# GConf manager
#
class ChristineGConf(Singleton):
	"""
	Gconf manager
	"""
	#
	# Constructor
	#
	def __init__(self):
		"""
		Constructor
		"""
		
		self.__Logger = ChristineLogger()

		self.setName('ChristineGConf')

		self.__Directory = '/apps/christine'

		self.__BoolKeys  = {
		                    'ui/small_view'      : False,
						    'ui/visualization'   : False,
						    'control/shuffle'    : False, 
						    'control/repeat'     : False,
						    'ui/show_artist'     : True, 
						    'ui/show_album'      : True,
						    'ui/show_play_count' : True,
						    'ui/show_tn'         : True,
						    'ui/show_length'     : True,
						    'ui/show_genre'      : True,
						    'ui/show_in_notification_area':True,
						    'ui/show_pynotify'   : True,
						    'ui/show_type'       : True
						    }

		self.__StringKeys = {
		                     'backend/audiosink' : 'autoaudiosink',
						     'backend/videosink' : 'ximagesink',
						     'backend/video-aspect-ratio' : '1/1', 
						     'backend/allowed_files' : 'mp3,ogg,avi,wmv,mpg,mpeg,mpe,wav', 
						     'backend/vis-plugin' : 'goom'
						     }

		self.__GConf = gconf.client_get_default()
		self.__GConf.add_dir(self.__Directory, gconf.CLIENT_PRELOAD_RECURSIVE)
		self.__GConf.set_error_handling(gconf.CLIENT_HANDLE_ALL)
		self.setDefaultValues()
		self.notifyAdd = self.__GConf.notify_add
		self.notify_add = self.__GConf.notify_add
	
	#
	# Sets default values
	#
	# @return void
	def setDefaultValues(self):
		"""
		Sets default values
		"""
		if (not self.getBool('has_initial_keys')):
			self.setValue('has_initial_keys', True)

			for key in self.__StringKeys.keys():
				self.setValue(key, self.__StringKeys[key])

			for key in self.__BoolKeys.keys():
				self.setValue(key, self.__BoolKeys[key])	
	
	#
	# get item
	#
	# @return void
	def __getitem__(self, key, value):
		"""
		__getitem__
		"""
		pass	
	
	#
	# Toggle widget
	#
	# @return void
	def toggleWidget(self, client, cnx_id, entry, widget):
		"""
		Toggle widget
		"""
		widget.set_active(entry.get_value().get_bool())
	
	#
	# Toggle visible
	#
	# @return void
	def toggleVisible(self, client, cnx_id, entry, widget):
		"""
		Toggle visible
		"""
		value = entry.get_value().get_bool()
		if (type(widget) != gtk.TreeViewColumn):
			if (value):
				widget.show()
			else:
				widget.hide()
		elif (type(widget) == gtk.TreeViewColumn):
			widget.set_visible(value)
		else:
			raise TypeError('How should I show/hide this widget: ', widget)
	
	#
	# Toggle
	#
	# @return void
	def toggle(self, widget, entry):
		"""
		Toggle
		"""
		self.setValue(entry, widget.get_active())
	
	#
	# Gets data
	#
	# @param  string key
	# @return string
	def get(self, key):
		"""
		Gets data
		"""
		return self.__GConf.get(os.path.join(self.__Directory, key))

	#
	# Gets boolean data
	#
	# @param  string key
	# @return boolean
	def getBool(self, key):
		"""
		Gets boolean data
		"""
		return self.__GConf.get_bool(os.path.join(self.__Directory, key))

	#
	# Gets string data
	#
	# @param  string key
	# @return string
	def getString(self, key):
		return self.__GConf.get_string(os.path.join(self.__Directory, key))
	
	#
	# Gets integer data
	#
	# @param  string key
	# @return integer
	def getInt(self, key):
		return self.__GConf.get_int(os.path.join(self.__Directory, key))
	
	#
	# Gets float data
	#
	# @param  string key
	# @return float
	def getFloat(self, key):
		return self.__GConf.get_float(os.path.join(self.__Directory,key))

	#
	# Sets value data
	#
	# @param  string key
	# @return boolean
	def setValue(self, key, value):
		"""
		Sets value from a key
		"""
		self.__Logger.Log("Setting value %s to key %s"%(repr(value),key))
		if (isInteger(value)):
			self.__GConf.set_int(os.path.join(self.__Directory, key), value)
		elif (isString(value)):
			self.__GConf.set_string(os.path.join(self.__Directory, key), value)
		elif (isBoolean(value)):
			self.__GConf.set_bool(os.path.join(self.__Directory, key), value)
		elif (isFloat(value)):
			self.__GConf.set_float(os.path.join(self.__Directory, key), value)
		else:
			msg = "Error: value is not int, bool or string: %s" % value
			self.__Logger.Log(msg)
			raise TypeError(msg)





