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

#
# This module define the classes and procedures to use SQLite3 on christine
#

import sqlite3
from libchristine.globalvars import DBFILE
from libchristine.pattern.Singleton import Singleton

class sqlite3db(Singleton):
	def __init__(self):
		'''
		Constructor
		'''
		#create the 'connection'
		self.connection = sqlite3.connect(DBFILE)
		self.cursor = self.connection.cursor()
		if not self.get_db_version():
			self.createSchema()

	def execute(self, strSQL):
		'''
		Ejecuta una sentencia SQL enviando la sentencia al logger
		@param strSQL:
		'''
		self.__logger.debug(strSQL)
		self.cursor.execute(strSQL)

	def commit(self):
		'''
		Do a self.connection.commit storing the event in the log.
		'''
		self.__logger.info('Doing a commit')
		self.connection.commit()


	def get_db_version(self):
		'''
		Look for the version of the database schema. If it can't get the
		database version then it returns False
		'''
		strSQL = 'SELECT version FROM registry'
		try:
			self.execute(strSQL)
			return self.cursor.fetch_all()
		except: return False

	def createSchema(self):
		'''
		Create the default schema for the cristine data base
		'''
		tabledesc =[
		'CREATE TABLE registry (id INTEGER PRIMARY KEY, desc VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL)',
		'CREATE TABLE items (id INTEGER PRIMARY KEY, path text NOT NULL, \
						title NOT NULL, artist VARCHAR(255), \
						album VARCHAR(255), time VARCHAR(10), \
						playcount INTEGER NOT NULL, \
						rate ENUM(1,2,3,4,5))',
		'CREATE TABLE playlists (id INTEGER PRIMARY KEY, name VARCHAR(255))'
		'CREATE TABLE playlist_relation (id INTEGER PRIMARY KEY, \
					playlistid INTEGER NOT NULL, itemid INTEGER NOT NULL)',
		'CRATE TABLE radio (id INTEGER NOT NULL, title VARCHAR(30) NOT NULL,\
					url VARCHAR(255) NOT NULL, rate ENUM(1,2,3,4,5))',
		]

		for strSQL in tablesdesc:
			self.execute(strSQL)
			self.commit()

	def additem(self, path, title, artist='', album='', time='00:00'):
		'''
		Add a new item to the library
		@param path: The path where the file may be located
		@param title: The title of the
		@param artist: the name of the artist
		@param album: the name of the album
		@param time: the time of the item

		@return : The last row id.
		'''
		strSQL = 'INSERT INTO items values(null, %s,%s,%s,%s,%s,0,1)'%(path,
												title, artist, album, time)
		self.execute(strSQL)
		self.commit()
		return self.cursor.lastrowid

	def addPlaylist(self, name):
		'''
		Add a new playlist to the list of playlists

		@param name: name of the playlists
		@return: The playlist id
		'''
		strSQL = 'INSERT INTO playlists values(null, %s)'%name
		self.execute(strSQL)
		self.commit()
		return self.cursor.lastrowid

	def addItemtoPlaylist(self, itemid, playlistid):
		'''
		Add an item to the playlists

		@param itemid: id of the item
		@param playlistid: id of the playlist

		@return : None
		'''
		strSQL = 'INSERT INTO playlist_relation values \
					(null, %d, %d)'%(playlistid, itemid)
		self.execute(strSQL)
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

	def getItemsForPlaylist(self, playlistid):
		'''
		Return all the items on a given playlist
		@param playlistid: id of the playlist
		'''
		strSQL = 'SELECT a.path, a.title, a.album, a.artist, a.time, \
					a.playcount, a.rate FROM items as a \
					INNER JOIN playlist_relation as b  \
					ON a.id = b.itemid \
					INNER JOIN playlist as c ON \
					c.id = b.playlistid \
					WHERE b.playlistid = %d'%(playlistid)

		self.execute(strSQL)
		return self.cursor.fetch_all()






