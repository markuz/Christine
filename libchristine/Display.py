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
# @category  libchristine
# @package   Display
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

import gtk
import cairo
import pango
import gobject
from libchristine.Validator import *

BORDER_WIDTH  = 3
POS_INCREMENT = 3
LINE_WIDTH    = 2

#
# Test for writting a custom gtk-cairo widget 
#
class Display(gtk.DrawingArea):
	"""
	Test for writting a custom gtk-cairo widget
	"""
	
	#
	# Constructor
	#
	# @param  string text
	# @return void
	def __init__(self, text= ''):
		"""
		Constructor
		"""
		# since this class inherits methods and properties
		# from gtk.Drawind_area we need to initialize it too
		gtk.DrawingArea.__init__(self)

		# This flag is supposed to be used to check if the
		# display y being drawed
		self.__Drawing = False
		self.__HPos = 0

		# Adding some events
		self.set_property('events', gtk.gdk.EXPOSURE_MASK |
								    gtk.gdk.POINTER_MOTION_MASK |
								    gtk.gdk.BUTTON_PRESS_MASK)

		self.connect('button-press-event', self.__buttonPressEvent)
		self.connect('expose-event',       self.exposeEvent)

		gobject.signal_new('value-changed', self,
				           gobject.SIGNAL_RUN_LAST,
				           gobject.TYPE_NONE,
				           (gobject.TYPE_PYOBJECT,))

		self.__Song           = ""
		self.__Text           = ""
		self.__WindowPosition = 0
		self.__Value          = 0
		self.value = self.__Value

		self.setText(text)
		self.set_size_request(300, 42)
		gobject.timeout_add(250,self.__emit)
	
	def __emit(self):
		'''
		Emits an expose event
		'''

		self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))
		#self.emit("expose-event",self)
		return True

	#
	# callback when a button is pressed
	#
	def __buttonPressEvent(self, widget, event):
		"""
		Called when a button is pressed in the display
		"""
		(x, y)       = self.get_pointer()
		(minx, miny) = self.__Layout.get_pixel_size()
		minx         = miny
		width        = (self.__W - miny - (BORDER_WIDTH * 3))
		miny         = (miny + (BORDER_WIDTH * 2))
		maxx         = (minx + width)
		maxy         = (miny + BORDER_WIDTH)

		if ((x >= minx) and (x <= maxx) and (y >= miny) and (y <= maxy)):
			value = (((x - minx) * 1.0) / width)
			self.setScale(value)
			self.__emit()
			self.emit("value-changed",self)


	#
	# Sets text
	#
	# @param  string text
	# @return void
	def setText(self, text):
		"""
		Sets text
		"""
		self.__Text = text.encode('latin-1')

	#
	# Sets song
	#
	# @param  string song
	# @return void
	def setSong(self, song):
		"""
		Sets song
		"""
		if (not isString(song)):
			raise TypeError('Paramether must be text')
		try:
			self.__Song = u'%s'%song.encode('latin-1')
		except:
			self.__Song = song

	#
	# Gets value
	#
	# @return integer
	def getValue(self):
		"""
		Gets value
		"""
		return self.__Value
		
	#
	# Sets value
	#
	# @param  integer value
	# @return void
	def setValue(self, value):
		self.__Value = value

	#
	# Sets scale value
	#
	# @param  integer value
	# @return void
	def setScale(self, value):
		"""
		Sets scale value
		"""
		try:
			value = float(value)
		except ValueError, a:
			raise ValueError(a)
		if ((value > 1.0) or (value < 0.0)):
			raise ValueError('value > 1.0 or value < 0.0')

		self.__Value = value

		#self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))
	
	#
	# This function is used to draw the display
	#
	# @param  widget widget
	# @param  event  event
	# @return void
	def exposeEvent(self,widget,event):
		"""
		This function is used to draw the display
		"""
		style = self.get_style()
		tcolor = style.text[0]
		wcolor = style.bg[0]
		br,bg,bb = ((wcolor.red*1)/65000.0, 
				(wcolor.green*1)/65000.0, 
				(wcolor.blue*1)/65000.0)

		fr,fg,fb = ((tcolor.red*1)/65000.0,
				(tcolor.green*1)/65000.0,
				(tcolor.blue*1)/65000.0)
		# Every speed improvement is really appreciated.
		if (self.__Drawing) or (self.window == None):
			return True

		self.__Drawing = True
		(x, y, w, h)   = self.allocation

		self.__X, self.__Y, self.__W, self.__H = (x, y, w, h)

		self.__Context = self.window.cairo_create()

		self.__Context.rectangle(BORDER_WIDTH, 
		                         BORDER_WIDTH,
			                     (w - (2 * BORDER_WIDTH)), 
			                     (h - (2 * BORDER_WIDTH)))
		
		self.__Context.clip()

		self.__Context.rectangle(BORDER_WIDTH, 
		                         BORDER_WIDTH,
			                     (w - (2 * BORDER_WIDTH)), 
			                     (h - (2 * BORDER_WIDTH)))
		
		self.__Context.set_source_rgb(br,bg,bb)
		self.__Context.fill_preserve()
		self.__Context.set_source_rgb(fr,fg,fb)
		#self.__Context.set_source_rgb(0, 0, 0)
		self.__Context.stroke()

		# Write text
		(x, y, w, h)   = self.allocation
		self.__Layout  = self.create_pango_layout(self.__Song)

		self.__Layout.set_font_description(pango.
				FontDescription('Sans Serif 8'))

		(fontw, fonth) = self.__Layout.get_pixel_size()
		
		if self.__HPos == 0 or fontw < w:
			self.__HPos = (w - fontw) / 2
		elif self.__HPos > (fontw-(fontw*2)):
			self.__HPos = self.__HPos - 3
		else:
			self.__HPos = w + 1
		self.__Context.move_to(self.__HPos, (fonth)/2)
		self.__Context.set_source_rgb(fr,fg,fb)
		self.__Context.update_layout(self.__Layout)
		self.__Context.show_layout(self.__Layout)

		(fw, fh) = self.__Layout.get_pixel_size()
		width    = ((self.__W - fh) - (BORDER_WIDTH * 3))

		self.__Context.set_antialias(cairo.ANTIALIAS_NONE)
		self.__Context.rectangle(fh, 
				((BORDER_WIDTH * 2) + fh), width, BORDER_WIDTH)
		self.__Context.set_line_width(1)
		self.__Context.set_line_cap(cairo.LINE_CAP_BUTT)
		#self.__Context.set_source_rgb(0, 0, 0)
		self.__Context.stroke()
		
		width = (self.__Value * width)

		self.__Context.rectangle(fh, 
				((BORDER_WIDTH * 2) + fh), width, BORDER_WIDTH)
		#self.__Context.set_source_rgb(0,0,0)
		self.__Context.fill_preserve()
		#self.__Context.set_source_rgb(0,0,0)
		self.__Context.stroke()

		layout         = self.create_pango_layout(self.__Text)
		(fontw, fonth) = layout.get_pixel_size()

		self.__Context.move_to(((w - fontw) / 2), ((fonth + 33) / 2))
		layout.set_font_description(
				pango.FontDescription('Sans Serif 8'))
		self.__Context.set_source_rgb(fr,fg,fb)
		self.__Context.update_layout(layout)
		self.__Context.show_layout(layout)

		self.__Drawing = False
		
	value = property(getValue, setScale)
