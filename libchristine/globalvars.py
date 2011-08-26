#!/usr/bin/env python
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
# Module that holds all christine global vars.
#

import os
import sys
import gtk
from libchristine.options import options
from libchristine import cglobalvars

VERSION =cglobalvars.VERSION
PROGRAMNAME = cglobalvars.PROGRAMNAME 
DATADIR = '/usr/local/share'
PREFIX = '/usr/local'
SYSCONFDIR = '/usr/local/etc'
def get_posix_config_dir():
    if os.environ.has_key('XDG_CONFIG_HOME'):
        USERDIR  = os.path.join(os.environ['XDG_CONFIG_HOME'],"christine")
    else: 
        USERDIR  = os.path.join(os.environ["HOME"],".config","christine")
    return USERDIR

def get_nt_config_dir():
    USERDIR = os.path.join(os.environ['APPDATA'],'christine')
    return USERDIR

func = [get_nt_config_dir, get_posix_config_dir][os.name == 'posix']
USERDIR = func()


IMAGEDIR = os.path.join(USERDIR,'cache_images')
PIDFILE = os.path.join(USERDIR,'christine.pid')

DBFILE = os.path.join(USERDIR,'christine.db')
LOGFILE  = os.path.join(USERDIR,"log")

CHRISTINE_AUDIO_EXT = sound = ["mp3","ogg","wma"]
CHRISTINE_VIDEO_EXT = video = ["mpg","mpeg","mpe","avi"]

opts = options()
# global PATH to share files required
# Ugly hack to make this work on win32
if opts.options.debug or os.name == 'nt':
    SHARE_PATH = os.path.join(os.getcwd())
    PLUGINSDIR = os.path.join(os.getcwd(),'libchristine','Plugins')
    ICONPATH = os.path.join(SHARE_PATH,'gui','icons')
else:
    SHARE_PATH = os.path.join('/usr/local/share', 'christine')
    PLUGINSDIR = os.path.join('/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages','libchristine','Plugins')
    ICONPATH =  os.path.join(SHARE_PATH,"icons")
GUI_PATH = os.path.join(SHARE_PATH,"gui")
LOCALE_DIR = os.path.join("/usr/local/share','locale")
BUGURL=cglobalvars.BUGURL
TRANSLATEURL = cglobalvars.TRANSLATEURL


icon_theme = gtk.icon_theme_get_default()
for i in os.walk(ICONPATH):
    directory = i[0]
    if not directory in icon_theme.get_search_path():
        icon_theme.append_search_path(directory)
