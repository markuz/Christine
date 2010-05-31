#!/usr/bin/env python

from libchristine.pattern.Singleton import Singleton
from libchristine.globalvars import PLUGINSDIR
from libchristine.Logger import LoggerManager
from libchristine.ui import interface
import sys
import os

class Manager(Singleton):
	'''
	This class is the manager for the plugins. Will load them and
	launch them if they are enabled
	'''
	def __init__(self):
		self.interface = interface()
		self.logger = LoggerManager().getLogger('PluginsManager')
		self.interface.plugins = self
		self.plugins = {}
		self.load_plugins()
		self.logger = self.interface.LoggerManager.getLogger('PluginsManager')

	def load_plugins(self):
		'''
		Search for the files and then use the __importByName to load them
		'''
		files = os.listdir(PLUGINSDIR)
		filteredf = [k for k in files if os.path.isdir(os.path.join(PLUGINSDIR, k)) and k not in ('.svn',)]
		for pluginname in filteredf:
			plugin = self.__importByName('libchristine.Plugins.%s'%pluginname,pluginname)
			if not plugin:
				continue
			try:
				func = getattr(plugin,pluginname, False)
				if func:
					instance = func()
					self.plugins[instance.name] = instance
			except Exception, e:
				self.logger.exception(e)


	def __importByName(self,modulename,name = None):
		'''
		Import a module by its name

		@param modulename: name of the package to import
		@param name: name of the module to import
		'''
		if name == None:
			lname = []
		else:
			lname = [name]
		try:
			self.logger.info('Importing %s - %s'%(modulename, lname))
			module = __import__(modulename,
						globals(), locals(), lname)
		except ImportError, e:
			self.logger.exception(e)
			return None
		return module
