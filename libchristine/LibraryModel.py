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
		return gtk.TREE_MODEL_LIST_ONLY#|gtk.TREE_MODEL_ITERS_PERSIST

#===============================================================================
#
#	def row_inserted(self, path, iter):
#		self.emit('row-inserted', path, iter)
#
#	def row_deleted(self, path, iter):
#		self.emit('row-deleted', path, iter)
#
#	def row_changed(self, path, iter):
#		self.emit('row-changed', path, iter)
#===============================================================================


	def append(self, *args):
		self.__data.append(self.__emptyData[:])
		iter = len(self.__data) -1
		path = (iter,)
		niter = self.get_iter(path)
		self.row_inserted(path, niter)
		if args:
			return self.set(iter, *args)
		self.invalidate_iters()
		return iter

	def prepend(self, *args):
		self.__data.insert(0,self.__emptyData[:])
		iter = 0
		path = (iter,)
		niter = self.get_iter(path)
		self.row_inserted(path, niter)
		if args:
			return self.set(iter, *args)
		self.invalidate_iters()
		return iter

	def set(self, iter, *args):
		return self.set_value(iter, *args)

	def set_value(self, iter, *args):
		if isinstance(iter, tuple):
			iter = iter[0]

		list = self.__data[iter]
		size = len(args)
		c = 0
		while c < size:
			list[args[c]] = args[c+1]
			c +=2
		path = (self.__data.index(list),)
		niter = self.get_iter(path)
		self.row_changed(path, niter)
		self.invalidate_iters()
		return iter

	def on_get_iter(self, rowref):
		if not isinstance(rowref, int) and rowref:
			try:
				rowref = int(rowref[0])
			except:
				rowref = self.__data.index(rowref)
		try:
			return self.__data[rowref]
		except:
			return None

	def on_get_path(self, rowref):
		if isinstance(rowref, tuple):
			return rowref[0]
		return self.__data.index(rowref)

	def on_get_column_type(self, n):
		return self.column_types[n]

	def on_get_value(self, rowref, column):
		if isinstance(rowref, tuple):
			rowref = rowref[0]
		elif isinstance(rowref,list):
			rowref = self.__data.index(rowref)
		try:
			value = self.__data[rowref][column]
			return value
		except:
			return None

	def on_iter_next(self, rowref):
		if not isinstance(rowref, int) and rowref:
			try:
				rowref = int(rowref[0])
			except:
				rowref = self.__data.index(rowref)

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
		return self.__data[n]

	def on_iter_children(self, rowref):
		if not isinstance(rowref, int) and rowref:
			rowref = rowref[0]
		if rowref:
			return None
		return self.__data[rowref]

	def on_iter_has_child(self, rowref):
		return False

	def on_iter_n_children(self, rowref):
		if not isinstance(rowref, int) and rowref:
			rowref = int(rowref[0])
		if rowref:
			return 0
		return len(self.__data)

	def on_iter_parent(self, child):
		return None


	def remove(self, path):
		try:
			self.__data.pop(path)
			self.row_deleted((path,))
			return True
		except:
			return False

	def __removeLast20(self,):
		for i in range(20):
			path = len(self.__data) -1
			if not self.remove(path):
				return False
		return True

	def clear(self):
		while 1:
			if not self.__removeLast20():
				break
		self.invalidate_iters()

class LibraryModel:
	'''This is a custom model that
	implements ListStore, Filter and Sortable
	models
	'''
	def __init__(self,*args):
		'''Constructor
		'''
		self.basemodel =  christineModel(*args)

	def createSubmodels(self):

		self.__filter = self.basemodel.filter_new()
		self.__sorted = gtk.TreeModelSort(self.__filter)

	def getModel(self):
		return self.__sorted

	def set_visible_func(self,obj):
		self.__filter.set_visible_func(obj)

	def refilter(self):
		self.__filter.refilter()

	def remove(self,iter):
		iter = self.__getNaturalIter(iter)
		if iter != None:
			self.basemodel.remove(self,iter)

	def getValue(self,iter,column):
		niter = self.__getNaturalIter(iter)
		if niter != None:
			return self.basemodel.get_value(niter,column)

	def Get(self,iter,*args):
		#niter = self.__getNaturalIter(iter)
		niter = iter
		if niter != None:
			return self.basemodel.get(self.basemodel.create_tree_iter(niter),*args)

	def setValues(self,iter,*args):
		#niter = self.__getNaturalIter(iter)
		niter = iter
		if niter != None:
			args1 = []
			for i in args:
				if isinstance(i,str):
					try:
						value = u'%s'%i.encode('latin-1')
					except:
						value = i
				else:
					value = i
				args1.append(value)
			args2 = tuple(args1)
			return self.basemodel.set(iter, *args2)

	def get_value(self, iter, column):
		'''
		Wrapper for the get_value method.
		@param iter:
		@param column:
		'''
		iter = self.__getNaturalIter(iter)
		if iter != None:
			return self.basemodel.get_value(iter, column)

	def append(self, *args):
		return self.basemodel.append(*args)

	def prepend(self, *args):
		return self.basemodel.prepend(*args)

	def get_iter_first(self):
		return self.basemodel.get_iter_first()

	def clear(self, *args):
		return self.basemodel.clear()


	def __getNaturalIter(self,iter):
		if self.basemodel.iter_is_valid(iter):
			return iter
		if not self.__sorted.iter_is_valid(iter):
			return None
		iter = self.__sorted.convert_iter_to_child_iter(None, iter)
		if self.basemodel.iter_is_valid(iter):
			return iter
		iter = self.__filter.convert_iter_to_child_iter(iter)
		if self.basemodel.iter_is_valid(iter):
			return iter
		return None

	def getIterValid(self,iter):
		if not isinstance(iter, gtk.TreeIter):
			return None
		return self.__getNaturalIter(iter)

