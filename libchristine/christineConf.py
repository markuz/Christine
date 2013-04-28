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
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
from ConfigParser import ConfigParser
from libchristine.pattern.Singleton import Singleton
from libchristine.Translator import translate
from libchristine.Logger import LoggerManager
from libchristine.globalvars import USERDIR
from libchristine.envelopes import deprecated
from libchristine.Storage.sqlitedb import sqlite3db
import gtk
import sys
import os



class christineConf(Singleton):
    '''
    This is the christine replace for the gconf module. Basicly it does what
    gconf do but in a more convenient way for christine, and stripping all
    the things that gconf has.

    This implies that using christine with this module, all config in
    the gconf module no longer work, you must use the config file stored
    in ~/.christine.conf

    The christine.conf file is a simple .ini file wich is handled by christine
    using the configParser module.

    This module serves as proxy to the configParser module, and it will know
    when any value is changed, then, __notify to any watcher.
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.filepath = os.path.join(USERDIR, 'christine.conf')
        self.configParser = ConfigParser()
        self.db = sqlite3db()
        self.__notify = {}
        if os.path.exists(self.filepath):
            if not os.path.isfile(self.filepath):
                msg = translate('%s is not a file'%self.filepath)
                sys.stderr.write(msg)
            f = open(self.filepath)
            self.configParser.readfp(f)
            f.close()
        else:
            self.create_basic_config_file()

    @deprecated
    def create_basic_config_file(self):
        self.setValue('ui/show_artist',True)
        self.setValue('ui/show_album',True)
        self.setValue('ui/show_play_count',True)
        self.setValue('ui/show_tn',True)
        self.setValue('ui/show_length',True)
        self.setValue('ui/show_genre',True)
        self.setValue('ui/show_in_notification_area',True)
        self.setValue('ui/show_pynotify',True)
        self.setValue('ui/show_type',True)
        self.setValue('ui/small_view',False)
        self.setValue('ui/visualization',False)
        self.setValue('ui/sidepanel',True)
        self.setValue('ui/LastFolder',USERDIR)
        self.setValue('control/shuffle',True)
        self.setValue('control/repeat',False)
        self.setValue('control/volume',0.8)
        self.setValue('backend/audiosink','autoaudiosink')
        sink =['autovideosink', 'xvimagesink'][os.name == 'posix']
        self.setValue('backend/videosink',sink)
        self.setValue('backend/video-aspect-ratio','1/1')
        self.setValue('backend/aspect-ratio','1/1')
        self.setValue('backend/allowed_files','mp3,ogg,avi,wmv,mpg,mpeg,mpe,wav')
        self.setValue('backend/vis-plugin','goom')
        self.setValue('backend/last_played','')
        return True
    
    @deprecated
    def exists(self, path):
        '''
        Creates a new section/key 
        @param path:
        '''
        sp = path.split('/')
        if len(sp) < 2:
            return False
        
        if self.configParser.has_section(sp[0]) and \
             self.configParser.has_option(sp[0], sp[1]):
            return True
    @deprecated
    def resetDefaults(self):
        '''
        reset to defaults. behaviour is the same that using
        create_basic_config_file
        '''
        return self.create_basic_config_file()
    @deprecated
    def toggleWidget(self, value, widget):
        '''
        Inverts the 'active' property in the widget using the value of the
        entry
        @param entry: connection entry
        @param widget: widget to work on
        '''
        widget.set_active(value)
    
    @deprecated
    def toggleVisible(self, value, widget):
        '''
        Toggles the 'visible' property in the widget using the value of the
        entry
        @param entry: the conection entry
        @param widget: widget to work on
        '''
        if not isinstance(widget, gtk.TreeViewColumn):
            if value:
                widget.show()
            else:
                widget.hide()
        elif isinstance(widget, gtk.TreeViewColumn):
            widget.set_visible(value)
        else:
            raise TypeError('How should I show/hide this widget: ', widget)

    @deprecated
    def toggle(self, widget, entry):
        '''
        Toggle the entry value according to widget
        @param widget:
        @param entry:
        '''
        self.setValue(entry, widget.get_active())
    
    @deprecated
    def get(self, key, method = None):
        '''
        Returns the value of a key
        @param key: Key to work on
        '''
        vals = key.split('/')
        if len(vals) != 2:
            raise KeyError('The given key is not valid')
            return False
        section, option = vals
        if method == None:
            method = self.configParser.get
        try:
            result = method(section, option)
        except Exception, e:
            result = None
        return result

    @deprecated
    def getBool(self, key):
        '''
        A convenience method which coerces the option in the specified
        section to a boolean value.
        @param key: key to work on
        '''
        try:
            result = self.get_value(key)
        except ValueError:
            val = self.get(key, self.configParser.getboolean)
            if val != None: 
                result =  val
            else: 
                result = False
            self.setValue(key, result)
        return result
    
    @deprecated
    def getString(self, key):
        '''
        A convenience method which coerces the option in the specified
        section to a string value.
        @param key: key to work on
        '''
        try:
            result = self.get_value(key)
        except ValueError:
            val = self.get(key)
            if val != None: 
                result = val
            else: 
                result = False
            self.setValue(key, result)
        return result
    
    @deprecated
    def getInt(self, key):
        '''
        A convenience method which coerces the option in the specified
        section to a integet number.
        @param key: key to work on
        '''
        try:
            result = self.get_value(key)
        except ValueError:
            val = self.get(key, self.configParser.getint)
            if val != None: 
                result =  val
            else: 
                result =  0
            self.setValue(key, result)
        return result
    
    @deprecated
    def getFloat(self, key):
        '''
        A convenience method which coerces the option in the specified
        section to a floating point number.
        @param key: key to work on
        '''
        try:
            result = self.get_value(key)
        except ValueError:
            val = self.get(key, self.configParser.getfloat)
            if val != None: 
                result =  val
            else: 
                result =  0.0
            self.setValue(key, result)
        return result
    
    def setValue(self, key, value):
        '''
        Set the value on the key.

        @param key: key to work on, must be in the section/option way
        @param value: value for the key
        '''
        self.db.set_registry(key, value)
        self.__executeNotify(key, value)
        #=======================================================================
        # vals = key.split('/')
        # if len(vals) != 2:
        #    raise KeyError('The given key is not valid')
        # type = {} 
        # section, option = vals
        # if self.configParser.has_section(section):
        #    if not isinstance(value, str):
        #        nvalue = str(value).lower()
        #    else:
        #        nvalue = value
        #    oldvalue = self.getString(key)
        #    if oldvalue == nvalue:
        #        return True
        #    self.configParser.set(section, option, nvalue)
        # else:
        #    self.configParser.add_section(section)
        #    self.configParser.set(section, option, value)
        # f = open(self.filepath,'w')
        # self.configParser.write(f)
        # f.close()
        # del f
        #=======================================================================
    
    @deprecated
    def __executeNotify(self, key, value):
        if not self.__notify.has_key(key):
            return False
        for i in self.__notify[key]:
            func = i[0]
            args = i[1]
            func(value, *args)
    
    @deprecated
    def notifyAdd(self, key, func, *args):
        '''
        Save the func reference in the __notify list to be run every time the
        value of the key changes.

        func(value, userdata..)

        @param key: key to be used
        @param func: func to execute
        @param *args: user data
        '''
        if not self.__notify.has_key(key):
            self.__notify[key] = []
        self.__notify[key].append((func, args))

    @deprecated
    def notify_add(self, key, func, *args):
        '''
        the same has notifyAdd
        @param key:
        @param func:
        '''
        self.notifyAdd(self, key, func, *args)


    def get_value(self, key,):
        #Lets check if we have it in database, if we have it then 
        #use it.
        return self.db.get_registry(key)
            




