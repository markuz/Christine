#! /usr/bin/env python
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



import gtk
import os
import os.path
import gtk.glade
import logging
from  libchristine.globalvars import DATADIR, PROGRAMNAME, SHARE_PATH

class glade_xml:
	def __init__(self,file,root=None):
		'''constructor, receives the name of the interface descriptor
		and then initialize gtk.glade.XML'''
		locale_dir = os.path.join(DATADIR, 'locale')
		gtk.glade.bindtextdomain(PROGRAMNAME,locale_dir)
		gtk.glade.textdomain(PROGRAMNAME)
		self.xml = gtk.glade.XML(file,root,None)
		self.get_widget = self.xml.get_widget

	def __getitem__(self,widget):
		'''
		returns the widget according to the name of the widget.
		This lets the instance work like a dictionary
		'''
		return self.xml.get_widget(widget)

	def signal_autoconnect(self,signals):
		'''
		Signal autoconnect wrapper.
		'''
		self.xml.signal_autoconnect(signals)

class GtkMisc:
	def __init__(self):
		self.__Logger = logging.getLogger('GtkMisc')
		self.wdir = SHARE_PATH

	def gen_pixbuf(self,imagefile):
		'''Create a pixbuf from  a file'''
		pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.wdir,imagefile))
		return pixbuf

	def set_image(self,widget,filename):
		image = gtk.Image()
		image.set_from_pixbuf(self.gen_pixbuf(filename))
		widget.set_image(image)

	def image(self,filename):
		image = gtk.Image()
		image.set_from_pixbuf(self.gen_pixbuf(filename))
		image.show()
		return image

	def set_toolbutton_image(self,widget,filename):
		image = self.image(filename)
		widget.set_icon_widget(image)

	def strip_XML_entities(self,text):
		entities = {"&":"&amp;",
				"<":"&lt;",
				">":"&gt;",
				}
		for i in entities.keys():
			text = text.replace(i,entities[i])
		return text

	def scalePixbuf(self, pixbuf, width, height):
		if type(pixbuf) != gtk.gdk.Pixbuf:
			raise TypeError('First argument must be gtk.gdk.Pixbuf got %s'%repr(pixbuf))

		if type(width) != int or type(height) != int:
			raise TypeError('width and height must be integers')
		pixbuf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
		return pixbuf
	
	def encode_text(self, text):
		'''
		Trata de encodificar el texto para ser usado por Gtk.
		@param text:
		'''
		try:
			for i in ('latin-1','iso8859-1', 'utf8'):
				text =  u'%s'%text.decode(i)
				text =  u'%s'%text.encode(i)
		except Exception, e:
			return text
		return text




class CairoMisc:
	def __init__(self):
		pass

	def getCairoColor(self, color):
		return color/65535.0

	def hex2float(self, hex):
		ret = []
		for i in range(4):
			ic = int(hex[i])
			ret.append(ic / 255.0)
		return ret

	def render_rect(self, cr, x, y, w, h, o):
		'''
		create a rectangle with rounded corners
		'''
		x0 = x
		y0 = y
		rect_width = w
		rect_height = h
		radius = 10 + o

		x1 = x0 + rect_width
		y1 = y0 + rect_height
		cr.move_to(x0, y0 + radius)
		cr.curve_to(x0, y0+radius, x0, y0, x0 + radius, y0)

		cr.line_to(x1 - radius, y0)
		cr.curve_to(x1-radius, y0, x1, y0, x1, y0 + radius)

		cr.line_to(x1, y1-radius)
		cr.curve_to(x1, y1-radius, x1, y1, x1 -radius, y1)

		cr.line_to(x0 +radius, y1)

		cr.curve_to(x0+radius, y1, x0, y1, x0, y1-radius -1)
		cr.close_path()

class error:
	def __init__(self,text):
		if os.path.isdir("./gui/"):
			path = "./gui"
		else:
			path = os.path.join(DATADIR,"christine","gui")
		xml = glade_xml(os.path.join(path,"Error.glade"))
		dialog		= xml["dialog"]
		error_label = xml["error"]
		error_label.set_text(text)
		dialog.run()
		dialog.destroy()
