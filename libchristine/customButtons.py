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
import math

import gtk
import gobject
from libchristine.GtkMisc import CairoMisc, GtkMisc
from libchristine.Share import Share

class christineButtons(gtk.HBox,CairoMisc, GtkMisc):
	'''
	This class creates the custom buttons that christine have.
	@autor: Marco Islas <markuz@islascruz.org>
	'''
	def __init__(self):
		'''
		Constructor.
		'''
		gtk.HBox.__init__(self)
		CairoMisc.__init__(self)
		GtkMisc.__init__(self)
		self.__share = Share()

		prev = christineButton('prevButton.png')
		play = christineButton('playButton.png')
		next = christineButton('nextButton.png')
		self.pack_start(prev)
		self.pack_start(play)
		self.pack_start(next)
		self.show_all()


class christineButton(gtk.DrawingArea, GtkMisc):
	def __init__(self, imagename):
		gtk.DrawingArea.__init__(self)
		GtkMisc.__init__(self)
		self.connect('expose-event', self.__do_expose)
		pixbuf = self.gen_pixbuf(imagename)
		self.__origPixbuf = self.scalePixbuf(pixbuf, 25,25)
		self.__pixbuf = self.__origPixbuf.copy()
		self.set_size_request(25,25)
		self.set_property('events', gtk.gdk.EXPOSURE_MASK |
								    gtk.gdk.POINTER_MOTION_MASK |
								    gtk.gdk.BUTTON_PRESS_MASK|
								    gtk.gdk.BUTTON_RELEASE_MASK)
		self.connect('button-press-event', self.__buttonPressEvent)
		self.connect('button-release-event', self.__buttonRelease)
		self.set_size_request(27,27)

	def __buttonPressEvent(self, widget, event):
		for i in range(30):
			self.__pixbuf.saturate_and_pixelate(self.__pixbuf, 0,	False)
		self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))

	def __buttonRelease(self, widget, event):
		self.__pixbuf = self.__origPixbuf.copy()
		self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))

	def __do_expose(self, widget, event):
		'''
		Handle the expose event for widget-drawing
		@param widget:
		@param event:
		'''
		context = self.window.cairo_create()
		x,y = (event.area.x,event.area.y)
		w,h = (85,35)
		context.set_source_pixbuf(self.__pixbuf, (w/2)-40,	(h - 25)/2)
		context.paint()






