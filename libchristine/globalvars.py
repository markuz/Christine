#!/usr/bin/env python

#
# Module that holds all christine global vars.
#

import os
import sys

VERSION = '0.2.0_t1'
PROGRAMNAME = 'christine'
DATADIR = '/usr/share'
PREFIX = '/usr'
SYSCONFDIR = '/usr/etc'
USERDIR  = os.path.join(os.environ["HOME"],".christine")

DBFILE = os.path.join(USERDIR,'christine.db')
LOGFILE  = os.path.join(USERDIR,"log")

CHRISTINE_AUDIO_EXT = sound = ["mp3","ogg","wma"]
CHRISTINE_VIDEO_EXT = video = ["mpg","mpeg","mpe","avi"]

# global PATH to share files required
if "--devel" in sys.argv:
	SHARE_PATH = os.path.join("./")
else:
	SHARE_PATH = os.path.join('/usr/share', 'christine')

GUI_PATH = os.path.join(SHARE_PATH,"gui")
LOCALE_DIR = "/usr/share/locale/"
BUGURL='https://bugs.launchpad.net/christine'