#! /usr/bin/env python
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


import os
import cPickle as pickle
from libchristine.globalvars import DATADIR, USERDIR
from libchristine.Storage.sqlitedb import sqlite3db
from libchristine.Logger import LoggerManager

class sanity:
	'''
		Make all the sanity checks
	'''
	def __init__(self):
		self.__check_christine_dir()
		self.__check_dir(os.path.join(USERDIR,"sources"))
		self.__check_dir(os.path.join(USERDIR,"uplugins"))
		if not os.path.exists(os.path.join(USERDIR,"uplugins","__init__.py")):
				f = open(os.path.join(USERDIR,"uplugins","__init__.py"),"w+")
				f.write("#python")
				f.close()
		if os.getgid() == 0:
			self.__check_dir(os.path.join(DATADIR,"christine","cplugins"))

	def __check_christine_dir(self):
		if not os.path.exists(USERDIR):
			os.mkdir(USERDIR)
		else:
			if os.path.isfile(USERDIR):
				os.unlink(USERDIR)
				self.__check_christine_dir()

	def __check_dir(self,dir):
		if not os.path.exists(dir):
			os.mkdir (dir)
		else:
			if os.path.isfile(dir):
				os.unlink(dir)
				self.__check_dir(dir)

class lib_library(object):
	def __init__(self,list):
		sanity()
		self.__logger = LoggerManager().getLogger('liblibrary')
		self.__db = sqlite3db()
		self.idlist = self.__db.PlaylistIDFromName(list)
		if self.idlist == None and list == 'music':
			self.__db.execute('INSERT INTO playlists VALUES (null, ?)',"music")
			self.idlist = self.__db.PlaylistIDFromName('music')
		if not self.idlist:
			self.idlist = self.__db.PlaylistIDFromName('music')
			if not self.idlist:
				self.__db.execute('INSERT INTO playlists VALUES (null, ?)',"music")
				self.idlist = self.__db.PlaylistIDFromName('music')
		self.idlist = self.idlist['id']
		self.list = list
		self.__files = self.__db.getItemsForPlaylist(self.idlist)
		self.__logger.debug(len(self.__files))

	def __setitem__(self,name,path):
		self.append(name,path)

	def __getitem__(self,key):
		return self.__files[key]

	def append(self,name,data):
		if type(data) != type({}):
			raise TypeError, "data must be a dict, got %s"%type(data)
		self.__files[name]=data
		self.__logger.debug(data)
		id = self.__db.additem(
						path = name,
						title = data['title'],
						artist = data['artist'],
						album = data['album'],
						time = data['time'],
						type = data['type'],
						genre = data['genre'],
						track_number = data['track_number']
						)
		self.__db.addItemToPlaylist(self.idlist, id)
		self.__db.commit()

	def updateItem(self, path, **kwargs):
		'''
		Updates the data of a item in the db.
		'''
		self.__db.updateItemValues(path, **kwargs)
		self.__db.commit()

	def keys(self):
		return self.__files

	def save(self):
		return 1
		self.__db.save(self.__files)
	
	def clean_playlist(self):
		self.__db.deleteFromPlaylist(self.idlist)

	def clear(self):
		self.__files.clear()

	def remove(self,key):
		'''
		Remove an item from the main dict and return True or False
		'''
		self.__db.removeItem(key,self.idlist)
		c = {}
		if key in self.keys():
			for i in self.keys():
				if i != key:
					c[i]= self.__files[i]
			self.__files = c.copy()
			return True
		return False

	def get_type(self,file):
		#TODO: Fixme, wher the hell is sound or video defined??
		ext = file.split(".").pop()
		if ext in sound:
			return "sound"
		if ext in video:
			return "video"

	def get_all(self):
		return self.__files

	def get_sounds(self):
		a = {}
		for i in self.keys():
			if self.__files[i]["type"] == "audio":
				a[i] = self.__files[i]
		return a

	def get_videos(self):
		a = {}
		for i in self.keys():
			if self.__files[i]["type"] == "video":
				a[i] = self.__files[i]
		return a

	def get_by_path(self, path):
		'''
		Return the info os a song in the given path, if path doesn't exists 
		then return None
		@param path: Path of the file to be looked.
		'''
		return self.__db.getItemByPath(path)

