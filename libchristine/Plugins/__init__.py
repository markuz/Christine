#!/usr/bin/env python

from libchristine.pattern.Singleton import Singleton
from libchristine.globalvars import PLUGINSDIR
from libchristine.ui import interface
import os

class Manager(Singleton):
	'''
	This class is the manager for the plugins. Will load them and
	launch them if they are enabled
	'''
	def __init__(self):
		self.interface = interface()
		self.interface.plugins = self
		self.plugins = {}
		self.load_plugins()
		self.logger = self.interface.LoggerManager.getLogger('PluginsManager')

	def load_plugins(self):
		'''
		Search for the files and then use the __importByName to load them
		'''
		files = os.listdir(PLUGINSDIR)
		filteredf = [k for k in files if k.endswith('py') \
					and not k.endswith('plugin_base.py') \
					and not k.endswith('__init__.py')]
		for i in filteredf:
			pluginname = os.path.split(i)[-1].split('.')[0]
			plugin = self.__importByName('libchristine.Plugins.'+pluginname, pluginname)
			if plugin:
				instance = plugin()
				self.plugins[instance.name] = instance


	def __importByName(self,modulename,name):
		'''
		Import a module by its name

		@param modulename: name of the package to import
		@param name: name of the module to import
		'''
		try:
			module = __import__(modulename,
						globals(), locals(), [name])
		except ImportError, e:
			self.logger.exception(e)
			return None
		return vars(module)[name]
