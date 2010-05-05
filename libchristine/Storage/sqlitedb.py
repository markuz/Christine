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
# @category  GTK
# @package   Preferences
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import gobject

#
# This module define the classes and procedures to use SQLite3 on christine
#

import sqlite3
from libchristine.globalvars import DBFILE
from libchristine.pattern.Singleton import Singleton
from libchristine.Logger import LoggerManager
from libchristine.ui import interface
from libchristine.gui.GtkMisc import GtkMisc

DBVERSIONS = (
				(0,2,0),
				(0,7,0),
			)

TYPEFUNCS = {
				'bool':bool,
				'list':list,
				'int':int,
				'float':float,
				'string':str,
				}

class sqlite3db(Singleton, GtkMisc):
	def __init__(self):
		'''
		Constructor
		'''
		#create the 'connection'
		GtkMisc.__init__(self)
		self.__logger = LoggerManager().getLogger('sqldb')
		self.connect()
	
	def connect(self):
		self.connection = sqlite3.connect(DBFILE)
		self.connection.isolation_level = None
		self.connection.row_factory = self.dict_factory
		self.connection.text_factory = str
		self.have_to_commit = False
		self.cursor = self.connection.cursor()
		self.cursor.row_factory = self.dict_factory
		if not self.check_version():
			self.__logger.debug('No se encontro la version de la base de datos.')
			self.__logger.debug(self.get_db_version())
			self.createSchema()
			self.fillRegistry()
		self.iface = interface()
		self.iface.db = self
		return True
	
	def check_version(self):
		try:
			version = self.get_registry('/core/dbversion')
			version = tuple(map(int, version.split(".")))
			print version
		except ValueError:
			version = (0,0,0)
		for i in DBVERSIONS:
			if version >= i:
				continue
			self.update_version(map(str, i ))
		return True

	def update_version(self, version):
		ver = '_'.join(version)
		update_func = getattr(self, '_update_%s'%ver, None)
		if update_func:
			update_func()


	def _update_0_7_0(self):
		'''
		Update database to 0.7.0
		'''
		sentences = (
				'ALTER TABLE registry ADD COLUMN key VARCHAR(255)',
				'ALTER TABLE registry ADD COLUMN type VARCHAR(10)',
				'UPDATE registry SET value="0.7.0", type="string",key="/core/dbversion" WHERE desc = "version"',
				)
		for strSQL in sentences:
			try:
				self.execute(strSQL)
				self.commit()
			except Exception, e:
				print e

	def get_registry(self,key):
		strSQL = '''SELECT * FROM registry WHERE key = ?'''
		try:
			res = self.execute(strSQL, key)
		except:
			raise ValueError('There is no key %s in registry'%key)
		result = self.fetchone()
		if not result:
			raise ValueError('The key \'%s\' is not in registry'%key)
		try:
			print ">>>>>>>>>>>>>>>>>>",(result,)
			t = result['type']
		except KeyError:
			raise ValueError('Database must be upgraded at least to 0.7.0')
		value = TYPEFUNCS[t](result['value'])
		return value
			
			
	def set_registry(self,key, value):
		'''
		Set the value of value in the registry identified by key,
		Automatically checks the type of value and set the type to the
		registry.
		I if key does not exists then this function will create it.
		@param strung key: Key to create/update 
		@param * value: value to be set
		'''
		#Check if the key exists
		try:
			val = self.get_registry(key)
		except ValueError:
			self.create_key_registry(key)
		strvalue = str(value)
		type = 'string'
		if isinstance(value, bool):
			type = 'bool'
		else:
			for k, t in TYPEFUNCS.iteritems():
				if isinstance(value, t):
					type = k
					break
		strSQL = '''
		UPDATE registry SET value = ?, type=? WHERE key = ?
		'''
		self.execute(strSQL,strvalue, type, key)
		self.commit()
	
	def create_key_registry(self, key):
		strSQL = '''
		INSERT INTO registry VALUES(null,'','',?,'string')
		'''
		self.execute(strSQL, key)
		self.commit()
		


	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			val = row[idx]
			if isinstance(val, str):
				val = self.encode_text(val)
			d[col[0]] = val
		return d

	def execute(self, strSQL,*args):
		'''
		Ejecuta una sentencia SQL enviando la sentencia al logger
		@param strSQL:
		'''
		tup = (strSQL, args)
		self.__logger.debug('Executing : %s',repr(tup))
		res = self.cursor.execute(strSQL,args)
		return res

	def fetchone(self):
		'''
		Wrapper for the fetchone cursor's method, but saves the value on the
		loger
		'''
		val = self.cursor.fetchone()
		return val

	def fetchall(self):
		'''
		Wrapper for the fetchall cursor's method, but saves the value on the
		loger
		'''
		val = self.cursor.fetchall()
		return val

	def fetchmany(self):
		'''
		Fecth all rows from a resultset, and saves the value on the logger.
		'''
		val = self.cursor.fetchmany()
		return val

	def commit(self):
		'''
		Do a self.connection.commit storing the event in the log.
		'''
		self.have_to_commit = True
	
	def do_commit(self):
		if self.have_to_commit:
			self.connection.commit()
			self.have_to_commit = False
		return True

	def get_db_version(self):
		'''
		Look for the version of the database schema. If it can't get the
		database version then it returns False
		'''
		return self.get_registry('/core/dbversion')

	def createSchema(self):
		'''
		Create the default schema for the cristine data base
		'''
		tabledesc =[
		'CREATE TABLE IF NOT EXISTS registry (id INTEGER PRIMARY KEY, desc VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL)',
		'CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, path text NOT NULL, \
						title VARCHAR(255) NOT NULL, artist VARCHAR(255), \
						album VARCHAR(255), time VARCHAR(10), \
						playcount INTEGER NOT NULL, \
						rate INTEGER, \
						type VARCHAR(30), \
						track_number INTEGER NOT NULL, \
						genre varchar(30), \
						have_tags bool \
						)',
		'CREATE TABLE IF NOT EXISTS playlists (id INTEGER PRIMARY KEY, name VARCHAR(255))',
		'CREATE TABLE IF NOT EXISTS playlist_relation (id INTEGER PRIMARY KEY, \
					playlistid INTEGER NOT NULL, itemid INTEGER NOT NULL)',
		'CREATE TABLE IF NOT EXISTS radio (id INTEGER NOT NULL, title VARCHAR(30) NOT NULL,\
					url VARCHAR(255) NOT NULL, rate INTEGER)',
		]

		for strSQL in tabledesc:
			self.execute(strSQL)
			self.commit()

	def fillRegistry(self):
		'''
		Rellena el registro con valores adecuados
		'''
		reglist = ['INSERT INTO registry VALUES (null, "version", "0.2")',
				'INSERT INTO playlists VALUES (null, \'music\')',
				'INSERT INTO playlists VALUES (null, \'queue\')']
		for strSQL in reglist:
			self.execute(strSQL)
			self.commit()

	def additem(self, **kwargs):
		'''
		Add a new item to the library
		@param path: The path where the file may be located
		@param title: The title of the
		@param artist: the name of the artist
		@param album: the name of the album
		@param time: the time of the item

		@return : The last row id.
		'''
		# Check if the item is not already in the registry.
		values = self.getItemByPath(kwargs['path'])
		if values:
			return values['id'];
		strSQL = 'INSERT INTO items VALUES(null,?,?,?,?,?,0,1,?,?,?,?)'
		self.execute(strSQL,
					kwargs['path'],
					kwargs['title'],
					kwargs['artist'],
					kwargs['album'],
					kwargs['time'],
					kwargs['type'],
					kwargs['track_number'],
					kwargs['genre'],
					kwargs.get('have_tags', False),
					)
		return self.cursor.lastrowid

	def updateItemValues(self, path, **kwargs):
		'''
		Updte in db the data of the given file.
		@param path:
		'''
		#Check if the media is in the db.
		self.execute('SELECT id FROM items WHERE path=?',path)
		presult = self.fetchone()
		if not presult:
			self.__logger.warning('We look for %s but we cant find it on the db', path)
			return None

		strk = []
		vals = []
		for i in kwargs:
			strk.append('%s=?'%i)
			vals.append(kwargs[i])
		strk = ','.join(strk)
		strSQL = 'UPDATE items SET %s where path=?'%strk
		vals.append(path)
		vals = tuple(vals)
		self.execute(strSQL,*vals)
		self.commit()

	def removeItem(self, path, playlist):
		'''
		Remove a item from a playlist
		@param path: Path of the item
		@param playlist: Id of the playlist
		'''
		self.execute('SELECT id FROM items where path=?',path)
		itemid = self.fetchone()
		if not itemid:
			return None
		strSQL = 'DELETE FROM playlist_relation WHERE playlistid=? and itemid=?'
		self.execute(strSQL, playlist, itemid['id'])
		self.commit()
		return True

	def addItemToPlaylist(self, playlist, itemid):
		'''
		Create a reference beetween a item to a playlist
		@param playlist: playlist
		@param itemid: ID of the item
		'''
		strSQL = 'INSERT INTO playlist_relation values(null, %d,%d)'%(playlist, itemid)
		self.execute(strSQL)

	def addPlaylist(self, name):
		'''
		Add a new playlist to the list of playlists

		@param name: name of the playlists
		@return: The playlist id
		'''
		strSQL = 'INSERT INTO playlists values(null, ?)'
		self.execute(strSQL,name)
		self.commit()
		return self.cursor.lastrowid

	def removePlayList(self, name):
		strSQL = 'SELECT id FROM playlists WHERE name = ?'
		self.execute(strSQL,name)
		id = self.fetchone()['id']
		if id:
			strSQL = 'DELETE FROM playlist_relation WHERE playlistid=?'
			self.execute(strSQL,id)
			strSQL = 'DELETE FROM playlists WHERE id=?'
			self.execute(strSQL,id)
		self.commit()

	def deleteItemFromPlaylist(self, itemid, playlistid):
		'''
		Delete an item from a playlist

		@param itemid: id of the item
		@param playlistid: id of the playlist
		'''
		strSQL = 'DELETE FROM playlist_relation WHERE itemid=%d AND \
					playlistid=%d'%(itemid, playlistid)
		self.execute(strSQL)
		self.commit()
	
	def deleteFromPlaylist(self, playlistid):
		'''
		Delete all items from a playlist
		@param plaulistid:
		'''
		strSQL = 'DELETE FROM playlist_relation WHERE \
					playlistid=%d'%(playlistid)
		self.execute(strSQL)
		self.commit()
		
	def getItemsForPlaylist(self, playlistid):
		'''
		Return all the items on a given playlist
		@param playlistid: id of the playlist
		'''
		strSQL = 'SELECT a.path, a.title, a.album, a.artist, a.time, \
					\na.playcount, a.rate, a.type, a.track_number, a.genre, \
					\na.have_tags \
					\nFROM items as a \
					\nINNER JOIN playlist_relation as b  \
					\nON a.id = b.itemid \
					\nINNER JOIN playlists as c ON \
					\nc.id = b.playlistid \
					\nWHERE b.playlistid = %d \
					\nORDER BY a.path'%(playlistid)

		self.execute(strSQL)
		r = self.cursor.fetchall()
		d = {}
		while r:
			value = r.pop(0)
			d[value['path']] = value
		return d

	def getItemByPath(self, path):
		'''
		Return the values of a item by the given path
		@param path: Ruta en la que se encuentra el archivo
		'''
		strSQL = 'SELECT * FROM items WHERE path=?'
		self.execute(strSQL,path)
		return self.fetchone()

	def PlaylistIDFromName(self, playlist):
		'''
		Return the playlist according to the name
		@param playlist: playlist name
		'''
		if not isinstance(playlist, str):
			return None
		strSQL = 'SELECT id FROM playlists WHERE name=?'
		self.execute(strSQL, playlist)
		return self.fetchone()

	def getPlaylists(self):
		'''
		Return the playlists
		'''
		strSQL = 'SELECT * FROM playlists WHERE name <> "queue" '
		self.execute(strSQL)
		return self.fetchall()		

	def getAlbums(self):
		'''
		Returns a list with all albums in the item list
		'''
		strSQL = 'SELECT artist as album FROM items WHERE album <> "" GROUP BY album'
		self.execute(strSQL)
		result = self.fetchall()
		tmplist = []
		for value in result:
			if value['album'].strip():
				tmplist.append(value['album'])
		tmplist.sort()
		return tmplist
	
	def getRadio(self):
		'''
		Return a list of radio stations
		'''
		strSQL = 'SELECT * FROM radio'
		self.execute(strSQL)
		result = self.fetchall()
		return result
	
	def get_radio_by_url(self, url):
		'''
	 	Look a radio station for its url
	 	@param url:
	 	'''
		strSQL = 'SELECT * FROM radio WHERE url = ?'
		self.execute(strSQL, url)
		result = self.fetchall()
		return result
	
	def add_radio(self, name, url):
		'''
		Add a radio station by its url
		@param url:
		'''
		strSQL = '''
		INSERT INTO radio values(0,?,?,'')
		'''
		self.execute(strSQL,name, url)
		result = self.fetchall()
		self.commit()
		return result
	
	def removeRadio(self, title):
		'''
		Deletes a radio station by it's title
		@param title:
		'''
		strSQL = '''
		DELETE FROM radio WHERE title = ?
		'''
		self.execute(strSQL, title)
		self.commit()
		return True

	def insert_music_playlist(self):
		'''
		Insert the music playlist
		'''
		self.execute('INSERT INTO playlists VALUES (null, ?)',"music")
		return True
