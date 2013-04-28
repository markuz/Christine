#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2010 Marco Antonio Islas Cruz
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
# @category  Multimedia
# @package   Christine
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

import os
import gst
import gobject
import mutagen.mp3, mutagen.oggvorbis
from libchristine.pattern.Singleton import Singleton
from libchristine.Logger import LoggerManager



class GsTagger(gobject.GObject):
    __gsignals__= {
                'io-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                tuple()),
                'gst-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                (gobject.TYPE_PYOBJECT,)),
                'end-of-stream' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                tuple()),
                'buffering' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                (gobject.TYPE_PYOBJECT,)),
                'found-tag' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                tuple()),
                }
    
    def __init__(self, tag_element = None):
        gobject.GObject.__init__(self)
        
        self.location = ''
        tag_element = None
        self.Tags = {}
        
        self.__Logger = LoggerManager().getLogger('baseTagger')
        
        if not tag_element:
            self.bin = gst.element_factory_make('playbin')
            audiosink = gst.element_factory_make('fakesink')
            self.bin.set_property('audio-sink', audiosink)
            #videosink = gst.element_factory_make('fakesink')
            #self.bin.set_property('video-sink', videosink)
            self.bus = self.bin.get_bus()
            self.bus.add_watch(self.handler_message)
    
    def set_location(self, file):
        self.bin.set_state(gst.STATE_NULL)
        self.bin.set_state(gst.STATE_READY)
        self.location = file
        self.Tags = {}
        if os.name == 'nt':
            p = file.split("\\")
            file = "/" + "/".join(p)
        import urllib
        nfile = 'file://' + urllib.quote(file)
        self.bin.set_property('uri', nfile)
        self.bin.set_state(gst.STATE_PLAYING)
        
        
    
    def handler_message(self, a, b, c = None, d = None):
        '''
        Handle messages frmo self.bus
        @param a:
        @param b:
        @param c:
        @param d:
        '''
        type_file = b.type
        if (type_file == gst.MESSAGE_ERROR):
            if not os.path.isfile(self.location):
                self.emit('io-error')
                print b.parse_error()[1]
                self.__Logger.error(b.parse_error()[1])
            else:
                self.emit('gst-error',b.parse_error()[1])
                print "else,",b.parse_error()[1]
                self.__Logger.error(b.parse_error()[1])
        if (type_file == gst.MESSAGE_EOS):
            self.emit('end-of-stream')
        elif (type_file == gst.MESSAGE_TAG):
            self.foundTagCallback(b.parse_tag())
            self.emit('found-tag')
            gobject.timeout_add(300, self.delete)
        return True
    
    def delete(self):
        self.bin.set_state(gst.STATE_NULL)
        del self
    
    def foundTagCallback(self, tags):
        """
        Callback to found tags
        """
        if len(tags.keys()):
            for i in tags.keys():
                if tags[i] != None:
                    self.Tags[i] = tags[i]
                    
    def __getitem__(self, key):
        return self.Tags[key]
    
    def get(self, key, default):
        return self.Tags.get(key, default)
            

class Track:
    def setSong(self, song):
        if not isinstance(song, basestring):
            raise ValueError("The first argument must be a string")
        self.Song = song
        self.Title = ""
        self.Artist = ""
        self.Album = ""
        self.Track = "" 
        self.Genre = ""
        self.Length = ""
        self.Bitrate = ""         
        
    def createDict(self):
        tags = {
                'title'   : self.Title,
                'artist'  : self.Artist,
                'album'   : self.Album,
                'track'   : self.Track,
                'genre'   : self.Genre,
                'length'  : self.Length,
                'bitrate' : self.Bitrate                         
               }
        return tags
    
    
 
class MP3Track(Singleton,Track):
    IDS = { "TIT2": "title",
            "TPE1": "artist",
            "TALB": "album",
            "TRCK": "track",
            "TDRC": "year",
            "TCON": "genre"
            }
    
    def getTag(self, id3, t):
        if not id3.has_key(t): return ""
        text = str(id3[t])
 
        text = text.replace("\n", " ").replace("\r", " ")
        return text
 
    def readTags(self,Song):
        self.setSong(Song)
        try:
            info = mutagen.mp3.MP3(self.Song)
        except Exception, e:
            self.Title = ''
            self.Artist = ''
            self.Album = ''
            self.Genre = ''
            self.Length = ''
            self.Bitrate = ''
            return self.createDict()
 
        self.Length = info.info.length
        self.Bitrate = info.info.bitrate
        try:
            id3 = mutagen.id3.ID3(self.Song)
            self.Title = self.getTag(id3, "TIT2")
            self.Artist = self.getTag(id3, "TPE1")
            self.Album = self.getTag(id3, "TALB")
            self.Genre = self.getTag(id3, "TCON")
 
            try:
                # get track/disc id
                track = self.getTag(id3, "TRCK")
                if track.find('/') > -1:
                    (self.Track, self.DiscId) = track.split('/')
                    self.Track = int(self.Track)
                    self.DiscId = int(self.DiscId)
                else:
                    self.Track = int(track)
 
            except ValueError:
                self.Track = 0
                self.DiscId = 0
 
            self.Year = self.getTag(id3, "TDRC")
 
        except:
            pass
        
        return self.createDict()
 
class OGGTrack(Singleton,Track):
    def getTag(self, f, tag):
        try:
            return unicode(f[tag][0])
        except:
            return ""
 
    def readTags(self,Song):
        self.setSong(Song)
        try:
            f = mutagen.oggvorbis.OggVorbis(self.Song)
        except mutagen.oggvorbis.OggVorbisHeaderError:
            return
 
        self.Length = int(f.info.length)
        self.Bitrate = int(f.info.bitrate / 1024)
 
        self.Artist = self.getTag(f, "artist")
        self.Album = self.getTag(f, "album")
        self.Title = self.getTag(f, "title")
        self.Genre = self.getTag(f, "genre")
        if self.getTag(f,"tracknumber").isdigit():
            self.Track = int(self.getTag(f, "tracknumber"))
        else:
            self.Track = 0
        self.DiscId = self.getTag(f, "tracktotal")
        self.Year = self.getTag(f, "date")
        
        return self.createDict()  
 
class FakeTrack(Singleton,Track):
    def readTags(self,song):
        self.setSong(song)
        return self.createDict()
 
 
class Tagger(Singleton):
    def readTags(self, song):
        '''
        Reat the tags of a given file
        @param song:
        '''
        if not isinstance(song, basestring):
            raise TypeError('The first argument must be string, got %s'%type(song))
        ext = song.split('.').pop().lower()
        objects = {'mp3':MP3Track, 'ogg':OGGTrack}
        obj = objects.get(ext, FakeTrack)
        self.Rola = obj() 
        return self.Rola.readTags(song)
    
    def taggify(self, file, msg):
        tags = self.readTags(file)
        for i in tags.keys():
            msg = msg.replace('_%s_'%i, str(tags[i]))
        return msg

