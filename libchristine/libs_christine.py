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

from libchristine.Storage.sqlitedb import sqlite3db
from libchristine.Logger import LoggerManager


class lib_library(object):
    def __init__(self,listname):
        self.__logger = LoggerManager().getLogger('liblibrary')
        self.__db = sqlite3db()
        self.idlist = self.__db.PlaylistIDFromName(listname)
        if self.idlist == None:
            self.__db.insert_music_playlist()
            self.idlist = self.__db.PlaylistIDFromName('music')
        self.idlist = self.idlist['id']
        self.list = listname
        self.orderby = 'path'
        self.sorttype = 'ASC'
        self.load_list()

    def load_list(self):
        self.__files = self.__db.getItemsForPlaylist(self.idlist)
    
    def __setitem__(self,id,path):
        self.append(id,path)

    def __getitem__(self,id):
        for i in self.__files:
           if i['id'] == id: 
               return i

    def iteritems(self):
        return self.__files.iteritems()

    def append(self,name,data):
        '''
        Append an item to the playlist
        '''
        if not isinstance(data, dict):
            raise TypeError("data must be a dict, got %s"%type(data))
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
        self.load_list()

    def updateItem(self, path, **kwargs):
        '''
        Updates the data of a item in the db.
        '''
        self.__db.updateItemValues(path, **kwargs)
        self.__db.commit()
        self.load_list()

    def clean_playlist(self):
        self.__db.deleteFromPlaylist(self.idlist)

    def clear(self):
        self.__files = tuple()

    def remove(self,key):
        '''
        Remove an item from the main dict and return True or False
        '''
        self.__db.removeItem(key,self.idlist)
        self.load_list()
        return True

    def get_all(self):
        return self.__files[:]

    def __get_item_by_type(self, types):
        a = {}
        for i in self.__files:
            if i["type"] == types:
                a[i] = i
        return a
    def get_sounds(self):
        return self.__get_item_by_type('audo')

    def get_videos(self):
        return self.__get_item_by_type('video')

    def get_by_path(self, path):
        '''
        Return the info os a song in the given path, if path doesn't exists 
        then return None
        @param path: Path of the file to be looked.
        '''
        return self.__db.getItemByPath(path)

