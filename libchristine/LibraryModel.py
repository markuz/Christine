#! /usr/bin/env python
# -*- coding: latin-1 -*-
import gobject

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
import gc

class christineModel(gtk.GenericTreeModel):
	'''
	Modulo basado en gtk.TreeModel que permite el manejo de datos de clientes
	de manera mas efectiva que en gtk.ListStore.
	'''
	def __init__(self, *args):
		gtk.GenericTreeModel.__init__(self)
		self.column_size = len(args)
		self.column_types = args
		self.__data = []
		self.__emptyData = map(lambda x: '', range(self.column_size))
		#self.__data.append(self.__emptyData)
		#self.set_property('leak-references',False)

	def destroy(self):
		'''
		Deletes everything
		'''
		try:
			self.invalidate_iters()
			del self.__data
			del self.__emptyData
		except:
			pass
		del self
		gc.collect()


	def get_flags(self):
		return self.on_get_flags()

	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

	def append(self, *args):
		self.__data.append(self.__emptyData[:])
		iter = len(self.__data) -1
		if args:
			self.set(iter, *args)
		return iter

	def set(self, iter, *args):
		if not isinstance(iter, int):
			return False
		list = self.__data[iter]
		size = len(args)
		c = 0
		while c < size:
			list[args[c]] = args[c+1]
			c +=2
		self.invalidate_iters()

	def on_get_iter(self, path):
		return path

	def on_get_column_type(self, n):
		return self.column_types[n]

	def on_get_value(self, rowref, column):
		if not isinstance(rowref, int):
			rowref = rowref[0]
		try:
			return self.__data[rowref][column]
		except:
			return None

	def on_iter_next(self, rowref):
		if not isinstance(rowref, int) and rowref:
			rowref = int(rowref[0])
		rowref +=1
		if not len(self.__data) > rowref:
			return None
		return rowref

	def on_get_n_columns(self):
		return self.column_size

	def on_iter_nth_child(self, rowref, n):
		if not isinstance(rowref, int) and rowref:
			rowref = rowref[0]
		if rowref:
			return None
		try:
			return self.__data[n]
		except IndexError:
			return  None

	def on_iter_children(self, rowref):
		if not isinstance(rowref, int) and rowref:
			rowref = rowref[0]
		if rowref:
			return None
		return self.__data[0]

	def on_iter_has_child(self, rowref):
		return False

	def on_iter_n_children(self, rowref):
		if not isinstance(rowref, int) and rowref:
			rowref = rowref[0]
		if rowref:
			return 0
		return len(self.__data)

	def clear(self):
		self.__data = []
		self.invalidate_iters()

class LibraryModel(christineModel):
	'''This is a custom model that
	implements ListStore, Filter and Sortable
	models
	'''
	def __init__(self,*args):
		'''Constructor
		'''
		christineModel.__init__(self,*args)

	def createSubmodels(self):
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
		christineModel.remove(self,iter)

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

	def get_value(self, iter, column):
		'''
		Wrapper for the get_value method.
		@param iter:
		@param column:
		'''
		iter = self.__getNaturalIter(iter)
		if iter:
			return christineModel.get_value(self, iter, column)


	def __getNaturalIter(self,iter):
		print (type(iter),iter)
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

