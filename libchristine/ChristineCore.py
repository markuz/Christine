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
# This module implementes the Christine core
# this is where all important parts of christine
# are called and the instance are stored
# ChristineCore class is a Singleton, which means that
# no matter where you call it it will be the same.
#

from libchristine.pattern.Singleton import Singleton
from libchristine.Logger import LoggerManager
from libchristine.Player import Player
from libchristine.Plugins import Manager
from libchristine.gui.Display import Display
from libchristine.Library import library,queue
from libchristine.sources_list import sources_list
from libchristine.christineConf import christineConf

class ChristineCore(Singleton):
	def __init__(self):
		self.logger = LoggerManager().getLogger('ChristineCore')
		#Crear la instancia del player
		self.Player = Player()
		self.Display = Display()
		self.mainLibrary  = library()
		self.Queue = queue()
		self.Plugins = Manager()
		self.sourcesList = sources_list()
		self.config = christineConf()
