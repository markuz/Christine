#! /usr/bin/env python
# Copyright (c) 2006 Marco Antonio Islas Cruz
# <markuz@islascruz.org>
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
import time
import gobject
from libchristine.ui import interface
(PATH,
		NAME,
		TYPE,
		PIX,
		ALBUM,
		ARTIST,
		TN,
		SEARCH,
		PLAY_COUNT,
		TIME,
		GENRE)=xrange(11)

(VPATH,
		VNAME,
		VPIX) = xrange(3)

QUEUE_TARGETS = [
		('MY_TREE_MODEL_ROW',gtk.TARGET_SAME_WIDGET,0),
		('text/plain',0,1),
		('TEXT',0,2),
		('STRING',0,3)
		]


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
		#@self.set_property('leak-references',True)
		self.interface = interface()

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

	def append(self, *args):
		self.__data.append(self.__emptyData[:])
		iter = len(self.__data) -1
		if args:
			return self.set_value(iter, *args)
		path = (iter,)
		niter = self.get_iter((iter,))
		self.row_inserted(path, niter)
		self.invalidate_iters()
		return iter

	def prepend(self, *args):
		self.__data.insert(0,self.__emptyData[:])
		iter = 0
		if args:
			return self.set_value(iter, *args)
		path = (iter,)
		niter = self.get_iter((iter,))
		self.row_inserted(path, niter)
		self.invalidate_iters()
		return iter

	def set(self, iter, *args):
		return self.set_value(iter, *args)

	def set_value(self, iter, *args):
		if isinstance(iter, tuple):
			iter = iter[0]
		elif isinstance(iter, gtk.TreeIter):
			path = self.get_path(iter)
			if path:
				iter = path[0]
			else:
				return False
		list = self.__data[iter]
		size = len(args)
		for c in range(0,size,2):
			list[args[c]] = args[c+1]
		niter = self.get_iter((iter,))
		self.row_changed(iter, niter)
		return iter

	def on_get_iter(self, rowref):
		try:
			return self.__data[rowref[0]]
		except:
			return None

	def on_get_path(self, rowref):
		return (self.__data.index(rowref), rowref[0])[isinstance(rowref, tuple)]

	def on_get_column_type(self, n):
		return self.column_types[n]

	def on_get_value(self, rowref, column):
		if isinstance(rowref,list):
			return self.__data[self.__data.index(rowref)][column]
		elif isinstance(rowref, tuple):
			return self.__data[rowref[0]][column]

	def on_iter_next(self, rowref):
		try:
			return self.__data[ self.__data.index(rowref) + 1 ]
		except:
			return None

	def on_get_n_columns(self):
		return self.column_size

	def on_iter_nth_child(self, rowref, n):
		if rowref:
			return None
		elif len(self.__data):
			return self.__data[n]

	def on_iter_children(self, rowref):
		if rowref:
			return None
		elif len(self.__data):
			return self.__data[0]
		
	def on_iter_has_child(self, rowref):
		return False

	def on_iter_n_children(self, rowref):
		if rowref:
			return 0
		return len(self.__data)

	def on_iter_parent(self, child):
		return None

	def search_iter_on_column(self, value, column):
		'''
		Devuelve una referencia de la fila de la primera ocurrencia de
		path en la columna indicada
		@param value: Value to compare
		@param column: Column number.
		'''
		enum = enumerate(self.__data)
		while 1:
			try:
				c,data = enum.next()
				if data[column] == value:
					return self.get_iter((c,))
			except StopIteration:
				break

	def remove(self, path):
		if isinstance(path, gtk.TreeIter):
			path = self.get_path(path)[0]
		try:
			self.__data.pop(path)
			self.row_deleted((path,))

			return True
		except:
			return False

	def __removeLast20(self,):
		for i in range(20):
			path = len(self.__data)-1
			if not self.remove(path):
				return False
		return True

	def clear(self):
		while 1:
			if not self.__removeLast20():
				break
		self.invalidate_iters()
		gc.collect()
	
class LibraryModel:
	'''This is a custom model that
	implements ListStore, Filter and Sortable
	models
	'''
	def __init__(self,*args):
		'''Constructor
		'''
		self.basemodel =  christineModel(*args)
		self.TextToSearch = ''

	def append(self, *args):
		return  self.basemodel.append(*args)

	def prepend(self, *args):
		return self.basemodel.prepend(*args)

	def createSubmodels(self):
		self.__filter = self.basemodel.filter_new()
		self.__sorted = gtk.TreeModelSort(self.__filter)
		self.__filter.set_visible_func(self.filter)

	def filter(self, model, iter):
		if not self.TextToSearch:
			return True
		value = model.get_value(iter, SEARCH)
		return value.lower().find(self.TextToSearch) >= 0 

	def getModel(self):
		return self.__sorted

	def set_visible_func(self,obj):
		self.__filter.set_visible_func(obj)

	def refilter(self):
		self.__filter.refilter()

	def remove(self,iter):
		iter = self.__getNaturalIter(iter)
		if iter != None:
			self.basemodel.remove(iter)
	
	def get_path(self, iter):
		iter = self.__getNaturalIter(iter)
		if iter != None:
			return self.basemodel.get_path(iter)
	
	def sorted_path(self, iter):
		return self.__sorted.get_path(iter)

	def getValue(self,iter,column):
		niter = self.__getNaturalIter(iter)
		if niter != None:
			return self.basemodel.get_value(niter,column)

	def Get(self,iter,*args):
		niter = iter
		if niter != None:
			return self.basemodel.get(self.basemodel.create_tree_iter(niter),*args)

	def __encode(self, item):
		if isinstance(item,str):
			try:
				value = u'%s'%item.encode('latin-1')
			except:
				value = item
		else:
			return item
		return value
	
	def setValues(self,iter,*args):
		niter = iter
		if niter != None:
			args2 = tuple(map( self.__encode, args))
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

	def get_iter_first(self):
		return self.basemodel.get_iter_first()

	def clear(self, *args):
		return self.basemodel.clear()

	def convert_natural_iter_to_iter(self, iter):
		if not self.basemodel.iter_is_valid(iter):
			return None
		try:
			iter = self.__filter.convert_child_iter_to_iter(iter)
			iter = self.__sorted.convert_child_iter_to_iter(None, iter)
			return iter	
		except:
			return None
	
	def convert_natural_path_to_path(self, path):
		path = self.__filter.convert_child_path_to_path(path)
		return path

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

	def search(self, search_string, column):
		iter = self.basemodel.search_iter_on_column(search_string, column)
		if iter:
			try:
				fiter = self.__filter.convert_child_iter_to_iter(iter)
				niter = self.__sorted.convert_child_iter_to_iter(None, fiter)
				if niter:
					return niter
			except:
				return None
		return None
	
	def __search(self, model, path, iter, userdata):
		'''
		This function is called every time that the model needs to do an 
		iteration over a foreach call.
		@param model: reference to self.model
		@param path: path in the current interation
		@param iter: iter in the current iteration
		@param userdata:  (user data)
		'''
		search_string, column = userdata
		value = model.get_value(iter, column)
		if value == search_string:
			self.__searchResult = iter
			return True

	def set(self, *args):
		'''
		Wrapper to the self.basemodel.set method
		'''
		self.basemodel.set(*args)
		
	def iter_next(self, iter):
		'''
		Trys to get a next iter for the sortable model.
		@param iter:
		'''
		if self.basemodel.iter_is_valid(iter):
			iter = self.basemodel.iter_next(iter)
		return iter
