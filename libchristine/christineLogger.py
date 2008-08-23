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
# @category  GTK
# @package   Preferences
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import os

import logging
import logging.handlers
from libchristine.globalvars import USERDIR
import sys

class christineLogger:
	'''
	Implements the christine logging facility.
	'''
	def __init__(self, loggername):
		'''
		Constructor
		'''
		self.__Logger = logging.getLogger(loggername)
		f = '%(asctime)s:%(levelname)-5s:%(name)-5s:%(lineno)4s: %(message)-80s'
		formatter = logging.Formatter(f)
		if '--verbose' in sys.argv:
			LOGGING_MODE = logging.DEBUG
			LOGGING_HANDLER = logging.StreamHandler()
		else:
			LOGGING_MODE = logging.DEBUG
			log = os.path.join(USERDIR, 'christine.log')
			LOGGING_HANDLER = logging.handlers.RotatingFileHandler(log,
													'a',31457280, 10)

		LOGGING_HANDLER.setFormatter(formatter)
		LOGGING_HANDLER.setLevel(LOGGING_MODE)
		self.__Logger.setLevel(LOGGING_MODE)
		self.__Logger.addHandler(LOGGING_HANDLER)

		self.info = self.__Logger.info
		self.debug = self.__Logger.debug
		self.warning = self.__Logger.warning
		self.exception = self.__Logger.exception
		self.critical = self.__Logger.critical