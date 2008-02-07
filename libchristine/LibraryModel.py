#! /usr/bin/env python
# -*- coding: latin-1 -*-

## Copyright (c) 2006 Marco Antonio Islas Cruz
## <markuz@islascruz.org>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


import gtk
import sys

class LibraryModel(gtk.ListStore):
	'''This is a custom model that 
	implements ListStore, Filter and Sortable
	models
	'''
	def __init__(self,*args):
		'''Constructor
		'''
		gtk.ListStore.__init__(self,*args)
		self.__sortColumnID = (None,None)
		#self.__model = self
		self.__filter = self.filter_new()
		self.__sorted = gtk.TreeModelSort(self.__filter)

	def getModel(self):
		return self.__sorted

	def set_visible_func(self,obj):
		self.__filter.set_visible_func(obj)

	def refilter(self):
		self.__filter.refilter()
	
	def remove(self,iter):
		iter = self.__getNaturalIter(iter)
		gtk.ListStore.remove(self,iter)
	
	def getValue(self,iter,column):
		niter = self.__getNaturalIter(iter)
		if niter != None:
			return self.get_value(niter,column)
	
	def Get(self,iter,*args):
		niter = self.__getNaturalIter(iter)
		if niter != None:
			return self.get(niter,*args)

	def setValues(self,iter,*args):
		niter = self.__getNaturalIter(iter)
		if niter != None:
			args1 = []
			for i in args:
				if type(i) == type(''):
					try:
						value = u'%s'%i.encode('latin-1')
					except:
						value = i
				else:
					value = i
				args1.append(value)
			args2 = tuple(args1)
			return self.set(niter, *args2)
	

	def __getNaturalIter(self,iter):
		if self.iter_is_valid(iter):
			return iter
		if not self.__sorted.iter_is_valid(iter):
			return None
		iter = self.__sorted.convert_iter_to_child_iter(None, iter)
		if self.iter_is_valid(iter):
			return iter
		iter = self.__filter.convert_iter_to_child_iter(iter)
		if self.iter_is_valid(iter):
			return iter 
		return None

	def getIterValid(self,iter):
		if type(iter) != gtk.TreeIter:
			return None
		return self.__getNaturalIter(iter)


