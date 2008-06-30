#!/usr/bin/env python

#
# Module that holds all christine global vars.
#

import os

VERSION = '0.2.0_t1'
PROGRAMNAME = 'christine'
DATADIR = '/usr/share'
PREFIX = '/usr'
SYSCONFDIR = '/usr/etc'
wdir = os.path.join(os.environ["HOME"],".christine")

DBFILE = os.path.join(wdir,'christine.db')

CHRISTINE_AUDIO_EXT = sound = ["mp3","ogg","wma"]
CHRISTINE_VIDEO_EXT = video = ["mpg","mpeg","mpe","avi"]

