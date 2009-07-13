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
from libchristine.CLibraryModel import CLibraryModel
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


class christineModel(CLibraryModel, gtk.GenericTreeModel, ):
	'''
	Modulo basado en gtk.TreeModel que permite el manejo de datos de clientes
	de manera mas efectiva que en gtk.ListStore.
	'''

	def __init__(self, *args):
		gtk.GenericTreeModel.__init__(self)
		CLibraryModel.__init__(self)
		self.column_size = len(args)
		self.column_types = args
		self.data = []
		self.__emptyData = map(lambda x: '', range(self.column_size))
		#@self.set_property('leak-references',True)
		self.interface = interface()
		#self.on_get_iter = CLibraryModel.on_get_iter
		self.set = self.set_value
		

	def destroy(self):
		'''
		Deletes everything
		'''
		try:
			self.invalidate_iters()
			del self.data
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
		self.data.append(self.__emptyData[:])
		path = len(self.data) -1
		if args:
			self.emit_inserted = True
			return self.set_value(path, *args)
		path = (path,)
		iter = self.get_iter(path)
		self.row_inserted(path, iter)
		self.invalidate_iters()
		self.__data_tuple = tuple(self.data)
		return iter

	def prepend(self, *args):
		self.data.insert(0,self.__emptyData[:])
		iter = 0
		if args:
			return self.set_value(iter, *args)
		path = (iter,)
		niter = self.get_iter((iter,))
		self.row_inserted(path, niter)
		self.invalidate_iters()
		self.__data_tuple = tuple(self.data)
		return iter

	def set_value(self, path, *args):
		if isinstance(path, tuple):
			path = path[0]
		elif isinstance(path, gtk.TreeIter):
			path = self.get_path(path)
			if not path:
				return False
			path = path[0]
		list = self.data[path]
		size = len(args)
		for c in xrange(0,size,2):
			list[args[c]] = args[c+1]
		iter = self.get_iter((path,))
		if self.emit_inserted:
			self.row_inserted(path, iter)
			self.emit_inserted = False
		self.row_changed(path, iter)
		self.__data_tuple = tuple(self.data)
		return iter

#===============================================================================
#	def on_get_iter(self, rowref):
#		try:
#			result =  CLibraryModel.on_get_iter(self, rowref)
#		except:
#			result = None
#		return result
#===============================================================================
	
#===============================================================================
#	def on_get_iter(self, rowref):
#		try:
#			result = self.data[rowref[0]]
#		except:
#			result = None
#		return result
#===============================================================================

	def on_get_path(self, rowref):
		if not isinstance(rowref, tuple):
			return self.data.index(rowref)
		else:
			return rowref[0]
			
	def on_get_column_type(self, n):
		return self.column_types[n]

	def get_index(self, ref):
		return self.data.index(ref)
		
	def on_get_value(self, rowref, column):
		rowref = self.data.index(rowref)
		return self.data[rowref][column]

	def on_iter_next(self, rowref):
		index = self.data.index(rowref)
		return self.data[ index + 1 ]

	def on_get_n_columns(self):
		return self.column_size

	def on_iter_nth_child(self, rowref, n):
		if rowref:
			return None
		elif len(self.data):
			return self.data[n]

	def on_iter_children(self, rowref):
		if rowref:
			return None
		elif len(self.data):
			return self.data[0]
		
	def on_iter_has_child(self, rowref):
		return False

	def on_iter_n_children(self, rowref):
		if rowref:
			return 0
		return len(self.data)

	def on_iter_parent(self, child):
		return None

	def search_iter_on_column(self, value, column):
		'''
		Devuelve una referencia de la fila de la primera ocurrencia de
		path en la columna indicada
		@param value: Value to compare
		@param column: Column number.
		'''
		for c, data in enumerate(self.data):
			if data[column] == value:
				return self.get_iter((c,)) 

	def remove(self, path):
		if isinstance(path, gtk.TreeIter):
			path = self.get_path(path)[0]
		if len(self.data):
			self.data.pop(path)
			self.row_deleted((path,))
			return True

	def __removeLast20(self,):
		for i in xrange(20):
			path = len(self.data)-1
			if not self.remove(path):
				return False
		return True

	def clear(self):
		while 1:
			if not self.__removeLast20():
				break
		self.invalidate_iters()
		self.__data_tuple = tuple(self.data)
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
		self.__sorted = gtk.TreeModelSort(self.basemodel)

	def getModel(self):
		return self.__sorted

	def remove(self,iter):
		iter = self.getNaturalIter(iter)
		if iter != None:
			self.basemodel.remove(iter)
	
	def get_path(self, iter):
		iter = self.getNaturalIter(iter)
		if iter != None:
			return self.basemodel.get_path(iter)
	
	def sorted_path(self, iter):
		return self.__sorted.get_path(iter)

	def getValue(self,iter,column):
		niter = self.getNaturalIter(iter)
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
		@param iter: gtk.TreeIter to get values
		@param column: Column number
		'''
		iter = self.getNaturalIter(iter)
		if iter != None:
			return self.basemodel.get_value(iter, column)

	def get(self, iter, *columns):
		'''
		Wrapper for the get_value method.
		@param iter: gtk.TreeIter to get values
		@param columns: Column numbers
		'''
		iter = self.getNaturalIter(iter)
		if iter != None:
			return self.basemodel.get(iter, *columns)

	def get_iter_first(self):
		return self.basemodel.get_iter_first()

	def clear(self, *args):
		result = self.basemodel.clear()
		return result

	def convert_natural_iter_to_iter(self, iter):
		if not self.basemodel.iter_is_valid(iter):
			return None
		try:
			iter = self.__sorted.convert_child_iter_to_iter(None, iter)
			return iter	
		except:
			return None
	
	def convert_natural_path_to_path(self, path):
		path = self.__filter.convert_child_path_to_path(path)
		return path

	def getNaturalIter(self,iter):
		if self.basemodel.iter_is_valid(iter):
			return iter
		if not self.__sorted.iter_is_valid(iter):
			return None
		iter = self.__sorted.convert_iter_to_child_iter(None, iter)
		if self.basemodel.iter_is_valid(iter):
			return iter
		return None

	def getIterValid(self,iter):
		if not isinstance(iter, gtk.TreeIter):
			return None
		return self.getNaturalIter(iter)

	def search(self, search_string, column):
		iter = self.basemodel.search_iter_on_column(search_string, column)
		if iter:
			niter = self.__sorted.convert_child_iter_to_iter(None, iter)
			if niter:
				return niter
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
		if isinstance(iter, gtk.TreeIter):
			if self.__sorted.iter_is_valid(iter):
				return self.__sorted.iter_next(iter)
	
	def iter_is_valid(self, iter):
		if isinstance(iter,gtk.TreeIter):
			return self.__sorted.iter_is_valid(iter)
		return False
	
