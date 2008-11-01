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


import logging
from libchristine.Validator import *
from libchristine.pattern.Singleton import Singleton
from libchristine.options import options

class LoggerManager(Singleton):
	def __init__(self):
		self.loggers = {}
	
	def getLogger(self, loggername):
		if not self.loggers.has_key(loggername):
			logger = Logger(loggername)
			self.loggers[loggername] = logger
		return self.loggers[loggername]

class Logger:
	'''
	Implements the christine logging facility.
	'''
	def __init__(self, loggername, type='event'):
		'''
		Constructor, construye una clase de logger.
		
		@param loggername: Nombre que el logger tendra.
		@param type: Tipo de logger. Los valores disponibles son : event y error
					por defecto apunta a event. En caso de utilizarse otro
					que no sea event o error se apuntara a event.
		'''
		opts = options()
		# Create two logger,one for info, debug and warnings and another for  
		# errors, exceptions and criticals
		self.__Logger = logging.getLogger(loggername)
		self.__ErrorLogger = logging.getLogger('Error'+ loggername)
		formatter = logging.Formatter('%(asctime)s:%(levelname)-8s:%(name)-10s:%(lineno)4s: %(message)-80s')
		level = 'DEBUG'
		nlevel = getattr(logging, level, None)
		if nlevel != None:
			LOGGING_MODE = nlevel
		else:
			LOGGING_MODE = logging.DEBUG
		if opts.options.debug:
			LOGGING_HANDLER = logging.StreamHandler()
			ERROR_HANDLER = logging.StreamHandler()
		else:
			LOGGING_HANDLER = logging.handlers.RotatingFileHandler('./christine_events.log','a',31457280, 10)
			ERROR_HANDLER = logging.handlers.RotatingFileHandler('./cristine_errors.log','a',31457280, 10)

		LOGGING_HANDLER.setFormatter(formatter)
		LOGGING_HANDLER.setLevel(LOGGING_MODE)
		ERROR_HANDLER.setFormatter(formatter)
		ERROR_HANDLER.setLevel(LOGGING_MODE)
		#Establecemos las propiedades de los loggers.
		self.__Logger.setLevel(LOGGING_MODE)
		self.__Logger.addHandler(LOGGING_HANDLER)
		
		self.__ErrorLogger.setLevel(LOGGING_MODE)
		self.__ErrorLogger.addHandler(ERROR_HANDLER)

		self.info = self.__Logger.info
		self.debug = self.__Logger.debug
		self.warning = self.__Logger.warning
		
		self.critical = self.__ErrorLogger.critical
		self.error = self.__ErrorLogger.error
		self.exception = self.__ErrorLogger.exception
	
