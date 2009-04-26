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



from libchristine.gui.GtkMisc import GtkMisc
from libchristine.ui import interface
from libchristine.christineConf import christineConf
from libchristine.Events import christineEvents

import gtk

christineConf = christineConf()

class plugin_base(object, GtkMisc):
	'''
	This is the base for the plugins for christine.
	Implements the basic methods for the plugins to work well with christine
	'''
	def __init__(self):
		self.name = 'Base Plugin'
		self.description = 'Here goes the plugin description'
		self.configurable = False #If christine should ask for the config dialog
		self.__active =  True
		self.interface = interface()
		self.christineConf = christineConf
		self.events = christineEvents()

	def configure(self):
		'''
		This method will be called when in the christine plugins preferences
		tab get the preferences button get pressed
		'''
		return None

	def get_active(self):
		self.__active

	def set_active(self, value):
		self.__active = value

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')
