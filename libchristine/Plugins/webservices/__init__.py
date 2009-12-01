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

#
# This module try to get the album cover and shows on the gui if it is found.
#

from libchristine.Plugins.plugin_base import plugin_base, christineConf
from libchristine.ui import interface
from libchristine.Share import Share
from libchristine.Tagger import Tagger
from libchristine.Translator import translate
from libchristine.Logger import LoggerManager
import SOAPpy
import thread

__name__ = translate('webservices')
__description__  = translate('Create a common webservice for christine.')
__author__  = 'Marco Antonio Islas Cruz <markuz@islascruz.org>'
__enabled__ = christineConf.getBool('webservices/getinfo')


class webservices(plugin_base):
	def __init__(self):
		'''
		Constructor
		'''
		plugin_base.__init__(self)
		self.name = __name__
		self.description =  __description__
		self.iface = interface()
		self.Share = Share()
		self.tagger = Tagger()
		self.logger = LoggerManager().getLogger("webservices")
		self.port = self.christineConf.getInt('webservices/port')
		self.webservices = SOAPpy.SOAPServer(('',self.port))
	
	def serve_forever(self):
		try:
			self.logger.info('starting webservices on port %s',str(self.port))
			self.soapserver.serve_forever()
		except Exception, e:
			self.logger.exception(e)
			self.logger.error('Reiniciando webservices')
			self.logger.info('Reiniciando webservices')
			self.create_server()
			thread.start_new(self.serve_forever, tuple())
			self.re_register_functions()	
	def re_register_functions(self):
		for function, x in self.function_dir.iteritems():
			self.soapserver.registerFunction(function)
			
	
	def registerFunction(self, function):
		self.soapserver.registerFunction(function)
		self.function_dir[function] = 1
	
	def registerObject(self,object):
		self.soapserver.registerObject(object)

	def get_active(self):
		return self.christineConf.getBool('webservices/enabled')
	
	def set_active(self, value):
		__enabled__ = value
		return self.christineConf.setValue('webservices/enabled', value)

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')
