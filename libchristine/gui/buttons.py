#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2009 Marco Antonio Islas Cruz
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
# @package   About
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2009 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

import gtk
import gobject
import math
import cairo
from libchristine.gui.GtkMisc import CairoMisc

class button(gtk.Button, CairoMisc):
	def __init__(self):
		gtk.Button.__init__(self,'')
		CairoMisc.__init__(self)
		self.__clicked =  False
		self.set_border_width(1)
		self.set_size_request(20,20)

		self.connect('button-press-event', self.__do_button_press)
		self.connect('button-release-event', self.__do_button_release)
		self.connect('expose-event', self.__do_expose)
	
	def __do_button_press(self, button, event):
		if event.button == 1:
			self.__clicked = True
			self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))

	def __do_button_release(self,button, event):
		if event.button == 1:
			self.__clicked =  False
			self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))
	
	def __do_expose(self, button, event):
		x, y, w, h =  self.allocation
		if not getattr(button, 'window', False):
			return 
		context = button.window.cairo_create()

		self.draw_arc(context)
		context.clip_preserve()
		linear = cairo.LinearGradient(x, y , x, h)
		activef = getattr(self, 'get_active', False)
		active = False
		if activef:
			active = activef()
		if not self.__clicked or not active:
			color = gtk.gdk.color_parse("#F8FBE2")
			colorbg = gtk.gdk.color_parse("#D6D0B7")
		else:
			colorbg = gtk.gdk.color_parse("#F8FBE2")
			color = gtk.gdk.color_parse("#D6D0B7")

		linear.add_color_stop_rgb(0.0,
						self.getCairoColor(color.red),
						self.getCairoColor(color.green),
						self.getCairoColor(color.blue),)
		linear.add_color_stop_rgb(1,
						self.getCairoColor(colorbg.red),
						self.getCairoColor(colorbg.green),
						self.getCairoColor(colorbg.blue))
		context.set_source(linear)
		context.fill_preserve()
		context.set_line_width(3)
		color2 = gtk.gdk.color_parse("#666")
		context.set_source_rgb(
						self.getCairoColor(color2.red),
						self.getCairoColor(color2.green),
						self.getCairoColor(color2.blue)
				)
		context.stroke()
	
	def draw_arc(self, context):
		x, y, w, h =  self.allocation
		if w > h:
			l = h 
		else:
			l = w 
		context.arc((w/2)+x, (h/2)+y, l/2, 0, 2*math.pi)

class next_button(button):
	def __init__(self):
		button.__init__(self)
		self.connect('expose-event', self.do_expose1)
		self.set_size_request(32,32)
	
	def do_expose1(self, button, event):
		x, y, w, h =  self.allocation
		#Dibujar triangulo de play:
		if not getattr(button, 'window', False):
			return 
		context = button.window.cairo_create()	
		self.draw_arc(context)
		context.clip()
		line_width = w * 0.1
		context.move_to(((w/5)*1.5)+x, (h/3)+y)
		context.line_to((w -(w/5))+x, (h/2)+y)
		context.line_to(((w/5)*1.5)+x, (h - (h/3))+y)
		context.close_path()
		context.fill()
		context.rectangle(((w/5)*3.5)+x, (h/2)-3+y, 2, 6)
		context.fill()
		return True

class prev_button(button):
	def __init__(self):
		button.__init__(self)
		self.connect('expose-event', self.do_expose1)
	
	def do_expose1(self, button, event):
		x, y, w, h =  self.allocation
		#Dibujar triangulo de play:
		if not getattr(button, 'window', False):
			return 
		context = button.window.cairo_create()	
		self.draw_arc(context)
		context.clip()
		context.move_to(((w/5)*3.5)+x, (h/3)+y)
		context.line_to(((w/5))+x, (h/2)+y)
		context.line_to(((w/5)*3.5)+x, (h - (h/3))+y)
		context.close_path()
		context.fill()
		context.rectangle((w/5)+x, (h/2)-3+y, 2, 6)
		context.fill()
		return True

class toggle_button(gtk.ToggleButton, button, CairoMisc):
	def __init__(self, *args, **kwargs):
		gtk.ToggleButton.__init__(self,*args, **kwargs)
		button.__init__(self)
		CairoMisc.__init__(self)
		self.connect('expose-event', self.do_expose1)

	def do_expose1(self, button, event):
		x, y, w, h =  self.allocation
		#Dibujar triangulo de play:
		if not getattr(button, 'window', False):
			return 
		context = button.window.cairo_create()	
		self.draw_arc(context)
		context.clip()
		context.move_to(((w/5)*1.5)+x, (h/3)+y)
		context.line_to((w -(w/5))+x, (h/2)+y)
		context.line_to(((w/5)*1.5)+x, (h - (h/3))+y)
		context.close_path()
		context.fill()
		return True

gobject.type_register(button)
gobject.type_register(next_button)
gobject.type_register(prev_button)
gobject.type_register(toggle_button)


if __name__ == '__main__':
	window = gtk.Window()
	window.set_position(gtk.WIN_POS_CENTER)
	window.connect('destroy', gtk.main_quit)
	b = button('')
	b.set_size_request(40,40)
	window.add(b),
	window.show_all()
	gtk.main()

