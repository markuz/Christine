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
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt


import time
import os
import gobject

from libchristine.Validator import *
from libchristine.GtkMisc import *
from libchristine.pattern.Singleton import Singleton


class ChristineLogger(Singleton,GtkMisc):
	'''
	This class helps in the christine logging functions
	'''
	def __init__(self):
		'''
		Contructor
		'''
		GtkMisc.__init__(self)
		self.__logs = []
		gobject.timeout_add(1000,self.__save)
	
	def log(self,text):
		if not isString(text) or isStringEmpty(text):
			raise TypeError("First argument must be a string, got %s"%type(text))
		text = time.ctime()+" "+text
		self.__logs.append(text)

	def __save(self):
		if len(self.__logs)==0:
			return True
		f = os.path.join(os.environ["HOME"],".christine","log")
		file = open(f,"a")
		file.write("\n".join(self.__logs)+"\n")
		file.close()
		self.__logs = []
		return True
