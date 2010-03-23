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
# @copyright 2006-2010 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

#
# This module implements the Christine main Windows
#
import gobject
from libchristine.ChristineCore import ChristineCore
#from libchristine.pattern.Singleton import Singleton
from libchristine.Share import Share

core = ChristineCore()

class mainWindow(gobject.GObject):
	def __init__(self):
		gobject.GObject.__init__(self)
		self.christineConf = core.config
		self.share = Share()
		self.build_gui()
		
	def build_gui(self):
		xml = self.share.getTemplate('WindowCore')
		self.mainWindow = xml['WindowCore']
		width = core.config.getInt('ui/width')
		height = core.config.getInt('ui/height')
		if not width or not  height:
			width, height = (800,600)
		self.mainWindow.set_default_size(width, height)
		#self.mainWindow.connect("destroy",lambda widget: widget.hide())
		#self.mainWindow.connect("scroll-event",self.changeVolumeWithScroll)
		#self.mainWindow.connect("key-press-event",self.onWindowkeyPressEvent)
		#self.mainWindow.connect('size-allocate', self.__on_corewindow_resized)

		self.mainWindow.show_all()

