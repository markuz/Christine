#! /usr/bin/env python
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
# @category  Multimedia
# @package   Christine
# @author    Maximiliano Valdez Gonzalez <garaged@gmail.com>
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

import  gobject
import dbus
from libchristine.ui import interface
from libchristine.Plugins.plugin_base import plugin_base,christineConf
from libchristine.Tagger import Tagger
from libchristine.Share import Share
from libchristine.christine_dbus import DBUS_SESSION
from libchristine.Translator import translate 
from libchristine.Logger import LoggerManager


__name__ = _('Pidgin')
__description__  = _('This plugin set the song you are playing on pidgin')
__author__  = ['Maximiliano Valdez Gonzalez <garaged@gmail.com>',
            'Marco Antonio Islas Cruz <markuz@islascruz.org>']
__enabled__ = christineConf.getBool('pidgin/enabled')

class pidgin(plugin_base):
    """
    Class to set pidgin's message, tests if pidgin and its dbus is accesible,
    and puts the current song played on the message
    """
    def __init__(self):
        self.logger = LoggerManager().getLogger('Plugin:Pidgin')
        plugin_base.__init__(self)
        self.name = __name__
        self.description =  __description__
        self.obj = None
        self.interface = interface()
        self.interface.Player.connect('player-play',self.set_message)
        self.Share = Share()
        self.SessionStart()
        self.tagger = Tagger()
        self.__create_conf_entries()
    
    def __create_conf_entries(self):
        if not self.christineConf.configParser.has_section('pidgin'):
            self.christineConf.configParser.add_section('pidgin')
        self.christineConf.configParser.set('pidgin','message',"_artist_ - _title_ - on Christine")

    def configure(self):
        '''
        This method will be called in the christine plugins preferences
        tab when pidgin's preferences button get pressed
        '''
        xml = self.Share.getTemplate('plugin_pidgin_main')
        self.dialog = xml['dialog']
        self.entry = xml['pidgin_message']
        self.entry.set_text(self.christineConf.configParser.get('pidgin','message'))
        self.entry.connect('changed', lambda widget: self.save_prefs())
        self.dialog.run()
        self.dialog.destroy()

    def save_prefs(self):
        message = self.entry.get_text()
        self.christineConf.setValue('pidgin/message',message)

    def window_destroy(self, button):
        self.dialog.destroy()

    def SetMessage(self,):
        file = self.christineConf.getString('backend/last_played')
        message = self.christineConf.getString('pidgin/message')
        if (not message):
            message = translate("Listening to: _title_ by _artist_ on Chrsitine")
            self.christineConf.setValue('pidgin/message', message)
        message = self.strip_XML_entities(self.tagger.taggify(file, message))
        if self.obj:
            try:
                current = self.purple.PurpleSavedstatusGetType(
                                    self.purple.PurpleSavedstatusGetCurrent())
                status = self.purple.PurpleSavedstatusNew("", current)
                self.purple.PurpleSavedstatusSetMessage(status, message)
                self.purple.PurpleSavedstatusActivate(status)
            except Exception, e:
                self.logger.exception(e)

    def SessionStart(self):
        try:
            self.obj = DBUS_SESSION.get_object("im.pidgin.purple.PurpleService",
                                            "/im/pidgin/purple/PurpleObject")
            self.purple = dbus.Interface(self.obj,
                                        "im.pidgin.purple.PurpleInterface")
            return True
        except Exception, e:
            self.logger.exception(e)
        return False

    def set_message(self, *args):
        """
        Convenient helper function to try the DBus connection if it's not
        already opened
        Could be done inside the self.SetMessage() but I don't
        like the idea, this is more flexible
        """
        if self.active:
            if  self.SessionStart():
                self.SetMessage()

    def get_active(self):
        return self.christineConf.getBool('pidgin/enabled')

    def set_active(self, value):
        __enabled__ = value
        return self.christineConf.setValue('pidgin/enabled', value)

    active = property(get_active, set_active, None,
                    'Determine if the plugin is active or inactive')
