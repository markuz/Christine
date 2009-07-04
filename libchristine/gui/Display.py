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
import gobject
import math
from libchristine.Validator import *
from libchristine.gui.GtkMisc import CairoMisc, GtkMisc
from libchristine.Events import christineEvents

BORDER_WIDTH  = 3
POS_INCREMENT = 3
LINE_WIDTH    = 2

class Display(gtk.DrawingArea, CairoMisc, GtkMisc, object):
	"""
	Display the track progress in christine
	"""


	def __init__(self, text= ''):
		"""
		Constructor
		"""
		# since this class inherits methods and properties
		# from gtk.Drawind_area we need to initialize it too
		gtk.DrawingArea.__init__(self)
		CairoMisc.__init__(self)
		GtkMisc.__init__(self)
		self.Events = christineEvents()

		self.__color1 = gtk.gdk.color_parse('#FFFFFF')
		self.__color2 = gtk.gdk.color_parse('#3D3D3D')


		# Adding some events
		self.set_property('events', gtk.gdk.EXPOSURE_MASK |
								    gtk.gdk.POINTER_MOTION_MASK |
								    gtk.gdk.BUTTON_PRESS_MASK)

		self.connect('expose-event',       self.__do_expose)
		self.connect('button-press-event', self.__buttonPressEvent)
		self.connect('configure-event', self.__on_size_allocate)


		gobject.signal_new('value-changed', self,
				           gobject.SIGNAL_RUN_LAST,
				           gobject.TYPE_NONE,
				           (gobject.TYPE_PYOBJECT,))

		self.__Song           = ""
		self.__Text           = ""
		self.__WindowPosition = 0
		self.__Value          = 0
		self.setText(text)
		self.set_size_request(150, 2)
		self.Events.addWatcher('gotTags', self.gotTags)
		self.do_screen_changed()
	
	def gotTags(self, tags):
		tooltext = tags['title']
		if (tags['artist'] != ''):
			tooltext    += " by %s" % tags['artist']
		if (tags['album'] != ''):
			tooltext    +=  " from %s" % tags['album']
		if tooltext:
			self.tooltext = tooltext
			self.setSong(tooltext)
			
	def __emit(self):
		'''
		Emits an expose event
		'''

		self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))

	def __buttonPressEvent(self, widget, event):
		"""
		Called when a button is pressed in the display
		"""
		(w, h)   = (self.allocation.width,self.allocation.height)
		(x, y)       = self.get_pointer()
		(minx, miny) = self.__Layout.get_pixel_size()
		minx         = miny
		width        = (w - miny - (BORDER_WIDTH * 3))
		miny         = (miny + (BORDER_WIDTH * 2))
		maxx         = (minx + width)
		maxy         = (miny + BORDER_WIDTH)

		if ((x >= minx) and (x <= maxx) and (y >= miny) and (y <= maxy)):
			value = (((x - minx) * 1.0) / width)
			self.setScale(value)
			self.emit("value-changed",self)

	def setText(self, text):
		"""
		Sets text
		"""
		self.__Text = self.encode_text(text)

	def setSong(self, song):
		"""
		Sets song
		"""
		if (not isString(song)):
			raise TypeError('Paramether must be text')
		self.__Song = u'%s'%self.encode_text(song)
		self.__emit()

	def getValue(self):
		"""
		Gets value
		"""
		return self.__Value

	def setValue(self, value):
		self.__Value = value

	def setScale(self, value):
		"""
		Sets scale value
		"""
		if value == self.value:
			return False
		try:
			value = float(value)
		except ValueError, a:
			raise ValueError(a)
		if ((value > 1.0) or (value < 0.0)):
			raise ValueError('value > 1.0 or value < 0.0')
		self.__Value = value
		self.__emit()

	def __on_size_allocate(self, widget,event):
		self.__HPos = event.x
	
	
	def do_screen_changed(self, old_screen=None):
		screen = self.get_screen()
		if self.is_composited():
			colormap = screen.get_rgba_colormap()
			self.supports_alpha = True
		else:
			#print 'Your schema doesn\'t support alpha channel'
			colormap = screen.get_rgb_colormap()
			self.supports_alpha = False
		self.set_colormap(colormap)
		
	def __do_expose(self,widget,event):
		if getattr(self,'window', None) == None:
			return False
		x,y,w,h = self.allocation
		x,y = (0,0)
		self.context = self.window.cairo_create()
		
		#if self.supports_alpha:
		#	self.context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
		#else:
		#	self.context.set_source_rgb(1.0, 1.0, 1.0)
			
		self.context.set_operator(cairo.OPERATOR_SOURCE)
		self.context.paint()
		self.context.move_to(0, 0)
		self.context.set_line_width(1.0)
		#self.context.set_operator(cairo.OPERATOR_OVER)
		
		
		#self.style = self.get_style()
		self.fontdesc = self.style.font_desc
		tcolor = self.style.fg[0]
		wcolor = self.style.bg[0]
		bcolor = self.style.bg[3]
		b1color = self.style.bg[2]
		self.br, self.bg, self.bb = (self.getCairoColor(wcolor.red),
				self.getCairoColor(wcolor.green),
				self.getCairoColor(wcolor.blue))
		self.fr , self.fg, self.fb = (self.getCairoColor(tcolor.red),
				self.getCairoColor(tcolor.green),
				self.getCairoColor(tcolor.blue))
		self.bar , self.bag, self.bab = (self.getCairoColor(bcolor.red),
				self.getCairoColor(bcolor.green),
				self.getCairoColor(bcolor.blue))
		self.bar1 , self.bag1, self.bab1 = (self.getCairoColor(b1color.red),
				self.getCairoColor(b1color.green),
				self.getCairoColor(b1color.blue))
		#clear the bitmap
		self.context.move_to( x, y )
		#self.context.set_operator(cairo.OPERATOR_OVER)
		self.context.set_line_width( 1 )
		self.context.set_antialias(cairo.ANTIALIAS_DEFAULT)
		self.context.rectangle(x,y,w,h)
		self.context.set_source_rgb(self.br,self.bg,self.bb)
		self.context.fill()
		self.draw_text(x,y,w,h)
		self.draw_progress_bar(x,y,w,h)
	
	def draw_progress_bar(self, x, y, w, h):
		fh = self.__Layout.get_pixel_size()[1]
		width    = ((w - fh) - (BORDER_WIDTH * 3))

		# Drawing the progress bar
		self.context.set_antialias(cairo.ANTIALIAS_NONE)
		self.context.rectangle(fh, ((BORDER_WIDTH * 2) + fh) +1 ,
						width, BORDER_WIDTH)
		self.context.set_line_width(1)
		self.context.set_line_cap(cairo.LINE_CAP_BUTT)
		self.context.set_source_rgb(1,1,1)
		self.context.fill_preserve()
		self.context.set_source_rgb(self.bar,self.bag,self.bab)
		self.context.stroke()

		width = (self.__Value * width)

		self.context.rectangle(fh, ((BORDER_WIDTH * 2) + fh)+1, width, BORDER_WIDTH)
		pat = cairo.LinearGradient(fh, ((BORDER_WIDTH * 2) + fh)+1, fh, 
								((BORDER_WIDTH * 2) + fh)+1 + BORDER_WIDTH)
		pat.add_color_stop_rgb(
							0.0,
							self.bar1,self.bag1,self.bab1
							)
		pat.add_color_stop_rgb(
							0.5,
							self.bar,self.bag,self.bab
							)
		self.context.set_source(pat)
		self.context.fill()
		self.context.set_source_rgb(self.bar,self.bag,self.bab)
		self.context.set_antialias(cairo.ANTIALIAS_DEFAULT)
		self.context.arc(int (fh + width),
				(BORDER_WIDTH * 2) + fh + (BORDER_WIDTH/2) +2, 4, 0, 2 * math.pi)
		self.context.fill()

		self.context.arc(int (fh + width),
				(BORDER_WIDTH * 2) + fh + (BORDER_WIDTH/2) +2, 2, 0, 2 * math.pi)
		self.context.set_source_rgb(1,1,1)
		self.context.fill()
	
	def draw_text(self, x, y, w , h):
		# Write text
		msg = ''
		if self.__Song:
			msg += self.__Song
		if self.__Text:
			msg += '--' + self.__Text
		self.__Layout  = self.create_pango_layout(msg)
		self.__Layout.set_font_description(self.fontdesc)
		(fontw, fonth) = self.__Layout.get_pixel_size()
		if self.__HPos == x or fontw < w:
			self.__HPos = (w - fontw) / 2
		elif self.__HPos > (fontw-(fontw*2)):
			self.__HPos = self.__HPos - 3
		else:
			self.__HPos = w + 1
		self.context.move_to(self.__HPos, (fonth)/2)
		self.context.set_source_rgb(self.fr,self.fg,self.fb)
		self.context.update_layout(self.__Layout)
		self.context.show_layout(self.__Layout)
		

	value = property(getValue, setScale)
