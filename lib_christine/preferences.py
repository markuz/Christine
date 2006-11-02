#! /usr/bin/env python
# -*- coding: UTF8 -*-

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


#import gtk,gobject
from lib_christine.libs_christine import *
from lib_christine.gtk_misc import *
from lib_christine.library import *


class preferences(gtk_misc):
	def __init__(self):
		gtk_misc.__init__(self)
		self.gconf = christine_gconf()
		self.xml = glade_xml("preferences.glade")
		self.audiosink = self.xml["audiosink"]
		self.videosink = self.xml["videosink"]
		self.select_sinks()
		dialog	 = self.xml["main_window"]
		dialog.set_icon(self.gen_pixbuf("logo.png"))
		dialog.run()
		dialog.destroy()

	def select_sinks(self):
		videosink = self.gconf.get_string("backend/videosink")
		audiosink = self.gconf.get_string("backend/audiosink")
		audio_m = self.audiosink.get_model()
		video_m = self.videonsink.get_model()
		for i in audio_m[0]:
			if i == audiosink:
				pass	
