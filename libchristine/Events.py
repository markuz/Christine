# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2008 Marco Antonio Islas Cruz
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
# @author    Maximiliano Valdez Gonzalez <garaged@gmail.com>
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
from libchristine.pattern.Singleton import Singleton
from libchristine.christineConf import christineConf
from libchristine.Logger import LoggerManager

class christineEvents(Singleton):
	'''
	This module generates events triggered by any other module in christine.

	The idea is generate a repository of functions to be called "onEvent", 
	to be used mainly by plugins that insert their functions to any event they 
	want/need.

	We want to replace the current scheme based on generating "events" by 
	changes on christineConf, that is not optimal, and it doesn't support a 
	variety of interesting events, namely "onPlay", "onStop", etc.

	This should probably be implemented with DBus library, but could make 
	Christine less portable

	Please change this doc after the module is complete.
	'''
	def __init__(self):
		'''
		Constructor: creates config if it doesn't exist
		'''
		self.__Logger = LoggerManager().getLogger('Events')
		self.christineConf = christineConf()
		if not self.christineConf.configParser.has_section('plugins'):
			self.christineConf.configParser.add_section('plugins')
			self.christineConf.setValue('plugins/enabled', True)
		self.__events = {}
		self.__watchers = {}

	def executeEvent(self, event):
		'''
		Event handler, executes functions associated to the given "event".

		Must be called on every relevant function (mainly by Player.py)
		'''
		if not self.__events.has_key(event):
			return False
		for i in self.__events[event]:
			func = i[0]
			args = i[1]
			func(*args)

	def addToEvent(self, event, func, *args):
		'''
		Adds a function to a given event (event) to be triggered by its 
		ocurrence as func(user_data...)

		@param event: event to be used
		@param func: func to execute
		@param *args: user data
		'''
		if not self.__events.has_key(event):
			self.__events[event] = []
		self.__events[event].append((func, args))
	
	def addWatcher (self, event, func):
		'''
		Add a watcher to an event
		@param event: nome of the event
		@param func: Function to be executed
		'''
		if not self.__watchers.has_key(event):
			self.__watchers[event] = []
		if callable(func):
			self.__watchers[event].append(func)
	
	def emit(self, event, *args):
		'''
		Emits the event
		@param event: The event to be emited
		@param *args: The args to be passed to the watchers
		'''
		if not self.__watchers.has_key(event):
			return False
		for func in self.__watchers[event]:
			func(*args)
		
		


