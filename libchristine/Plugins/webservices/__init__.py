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
# @sponsor	ICT Consulting <http://www.ictc.com.mx>
# @license   http://www.gnu.org/licenses/gpl.txt

#
# This module implements the webservices interface in christine
#
import SOAPpy
import os
from libchristine.Plugins.plugin_base import plugin_base, christineConf
from libchristine.ui import interface
from libchristine.Share import Share
from libchristine.Tagger import Tagger
from libchristine.Translator import translate
from libchristine.Logger import LoggerManager
from libchristine.ChristineCore import ChristineCore
from libchristine.gui.GtkMisc import Builder
from libchristine.globalvars import PLUGINSDIR
import gobject
import time
import thread
import gtk


__name__ = translate('webservices')
__description__  = translate('Create a common webservice for christine.')
__author__  = 'Marco Antonio Islas Cruz <markuz@islascruz.org>'
__enabled__ = christineConf.getBool('webservices/getinfo')


class webservices(plugin_base):
	def __init__(self):
		'''
		@sponsor	ICT Consulting <http://www.ictc.com.mx>
		'''
		plugin_base.__init__(self)
		self.name = __name__
		self.description =  __description__
		self.function_dir = []
		self.iface = interface()
		self.Share = Share()
		self.tagger = Tagger()
		self.logger = LoggerManager().getLogger("webservices")
		self.port = self.christineConf.getInt('webservices/port')
		self.core = ChristineCore()
		if self.active:
			self.start()
		
	
	
	def handle_request(self,source, condition):
		try:
			#self.soapserver.socket.setblocking(1)
			time.sleep(0.5)
			self.soapserver.handle_request()
		except Exception, e:
			self.logger.exception(e)
		return True
	
	def serve_forever(self):
		try:
			if not self.port:
				return
			self.soapserver = SOAPpy.SOAPServer(('',self.port))
			#self.soapserver.socket.setblocking(1)
			self.registerObject(self.set_location)
			self.re_register_functions()
			#gtk.gdk.threads_enter()
			#thread.start_new(self.soapserver.serve_forever, tuple())
			#gtk.gdk.threads_leave()
			
			gobject.io_add_watch(self.soapserver.socket, gobject.IO_IN,
			            self.handle_request)
		except:
			self.active = False

	def shutdown(self):
		if getattr(self, 'soapserver', False):
			self.soapserver.shutdown()
			self.soapserver.close()
	
	def start(self):
		self.serve_forever()
				
	def re_register_functions(self):
		for function in self.function_dir:
			self.soapserver.registerFunction(function)
			
	
	def registerFunction(self, function):
		self.soapserver.registerFunction(function)
		self.function_di.append(function)
	
	def registerObject(self,object):
		try:
			self.soapserver.registerObject(object)
		except:
			pass
		self.function_dir.append(object)

	def get_active(self):
		return self.christineConf.getBool('webservices/enabled')
	
	def set_active(self, value):
		__enabled__ = value
		if value:
			self.start()
		else:
			self.shutdown()
		return self.christineConf.setValue('webservices/enabled', value)
	
	def set_location(self, path):
		'''
		Play a song in the given path, path must be a Christine accesible path.
		@param string path: 
		'''
		def set_location1(self,path):
			if not path.lower().startswith('http'):
				if not os.path.exists(path) or not os.path.isfile(path):
					return 
			self.core.Player.stop()
			self.core.Player.set_location(path)
			self.core.Player.playIt()
			return False
		gobject.idle_add(set_location1, self, path)
		
	def play(self):
		self.core.Player.playIt()
		return True
	
	def pause(self):
		self.core.Player.pause()
		return True

	def configure(self):
		gladepath = os.path.join(PLUGINSDIR,'webservices','glade')
		path = os.path.join(gladepath, 'configure.glade')
		b = Builder(path)
		dialog = b['dialog']
		entry = b['portEntry']
		entry.set_text(str(self.port))
		dialog.connect('destroy', self.save_port_entry, entry)
		dialog.show()
		dialog.connect('response', lambda  *args: dialog.destroy())
		
	def save_port_entry(self, dialog, entry):
		if not entry.get_text().isdigit():
			return
		port = int(entry.get_text())
		self.core.config.setValue('webservices/port',port)
		self.port = port
		#self.shutdown()
		#if self.active:
		#	self.serve_forever()
		

	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')
