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
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

#
# This module is for testing christine debus functions.
#

import gtk
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import curses
curses.setupterm()
# Escape sequence used to clear the terminal
clear = curses.tigetstr('clear')
# Number of colours terminal supports
colours = curses.tigetnum('colors')
# Number of columns
columns = curses.tigetnum('cols')
# Number of lines
lines = curses.tigetnum('lines')

import sys
#sys.stdout.write(clear)
main_loop = DBusGMainLoop()



DBUS_SESSION = dbus.SessionBus(mainloop = main_loop)

obj = DBUS_SESSION.get_object('org.christine', '/org/christine',)
uri = obj.now_playing()
print uri
tags = obj.get_tags(uri)
print tags

def printLocation(newlocation):
    print newlocation
#obj.connect_to_signal('NewLocation', printLocation)
#===============================================================================
# options = {
#        'Play': obj.play,
#        'Pause': obj.pause,
#        'Go prev': obj.go_prev,
#        'Go next': obj.go_next,
#        }
# gtk.main()
# keys = ('Play', 'Pause', 'Go prev','Go next')
#===============================================================================
#    time.sleep(a
    
#===============================================================================
# for num, key in enumerate(keys):
#    print '%d - %s'%(num, key)
# value = raw_input()
# try: 
#    method = options[keys[int(value)]]
#    method()
#    sys.stdout.write(clear)
# except Exception, e:
#    pass
#===============================================================================
