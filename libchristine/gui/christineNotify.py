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
# This module includes the christine notify dialog.
#

import gtk
import cairo
import gobject
import pango
from libchristine.pattern.Singleton import Singleton
from libchristine.gui.GtkMisc import CairoMisc, GtkMisc
from libchristine.Share import Share


class notifyWindow(gtk.Window, GtkMisc, CairoMisc):
	def __init__(self):
		gtk.Window.__init__(self)
		CairoMisc.__init__(self)
		self.share = Share()
		self.pixbuf = self.share.getImageFromPix('logo')
		self.pixbuf = self.scalePixbuf(self.pixbuf, 20, 20)
		self.set_app_paintable(True)
		self.set_decorated(False)
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_skip_pager_hint(True)
		self.set_skip_taskbar_hint(True)
		self.set_resizable(False)
		self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
		self.do_screen_changed()
		self.connect( 'expose-event', self.__doExpose )
		self.label = gtk.Label()
		#self.label.set_font_desc('Lucida Grande 14')
		self.add(self.label)
		self.set_size_request(300,100)
	
	def set_text(self, text):
		self.text = text
		self.show_all()
		gobject.timeout_add(3000, self.__destroy)
	
	def __destroy(self, ):
		self.destroy()
		return False
		
	def do_screen_changed(self, old_screen=None):
		screen = self.get_screen()
		if self.is_composited():
			colormap = screen.get_rgba_colormap()
			self.supports_alpha = True
		else:
			print 'Your schema doesn\'t support alpha channel'
			colormap = screen.get_rgb_colormap()
			self.supports_alpha = False
		self.set_colormap(colormap)
	
	def __doExpose(self, widget, event):
		'''
		This will draw the notification...
		@param widget:
		@param event:
		'''
		cr = self.window.cairo_create()
		if self.supports_alpha:
			cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
		else:
			cr.set_source_rgb(1.0, 1.0, 1.0)
		
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		(width, height) = self.get_size()
		cr.move_to(0, 0)
		cr.set_line_width(1.0)

		cr.set_operator(cairo.OPERATOR_OVER)

		#pat = cairo.LinearGradient(0.0, 0.0, 0.0, height)
		
		style = self.get_style()
		bg1 = style.fg[1]
		bg1 = (self.getCairoColor(bg1.red), self.getCairoColor(bg1.green),
							self.getCairoColor(bg1.blue))
		bg2 = style.bg[3]
		bg2 = (self.getCairoColor(bg2.red), self.getCairoColor(bg2.green),
							self.getCairoColor(bg2.blue))
		gray = style.bg[1]
		gray = (self.getCairoColor(gray.red), self.getCairoColor(gray.green),
							self.getCairoColor(gray.blue))
		
		textcolors = style.text[0]
		textcolors =  (self.getCairoColor(textcolors.red), 
					self.getCairoColor(textcolors.green),
					self.getCairoColor(textcolors.blue))
		cr.set_source_rgba(bg2[0],bg2[1],bg2[2], 0.5)
		self.render_rect(cr, 0, 0, width, height, 5)
		cr.fill()
		cr.set_source_rgba(bg1[0],bg1[1],bg1[2],0.5)
		self.render_rect(cr, 1.5, 1.5, width - 3 , height - 3, 5)
		cr.stroke()
		cr.set_source_rgba(bg2[0],bg2[1],bg2[2], 0.5)
		self.render_rect(cr, 0.5, 0.5, width - 1 , height - 1, 5)
		cr.stroke()
		cr.set_source_rgba(gray[0],gray[1],gray[2], 0.5)
		self.render_rect(cr, 0, 0, width , height, 5)
		cr.stroke()
		cr.set_source_rgba(textcolors[0],textcolors[1],textcolors[2], 1.0)
		fd = self.get_style().font_desc
		fd.set_size(16 * pango.SCALE)
		layout = self.create_pango_layout('')
		layout.set_markup(self.text)
		layout.set_font_description(fd)
		w, h = layout.get_pixel_size()
		cr.move_to(width/2-w/2, height/2-h/2)
		cr.update_layout(layout)
		cr.show_layout(layout)
		cr.set_source_pixbuf(self.pixbuf, 3, 3 )
		cr.paint()

		for c in self.get_children():
			 self.propagate_expose(c, event)
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
