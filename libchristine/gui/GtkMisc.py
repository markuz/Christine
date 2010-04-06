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
import logging
from  libchristine.globalvars import DATADIR, PROGRAMNAME, SHARE_PATH


def load_rc():
	file = os.path.join(SHARE_PATH,'gui','gtkrc') 
	if not os.path.exists(file):
		return 
	gtk.rc_parse(file)
	gtk.rc_add_default_file(file)
	gtk.rc_reparse_all()

class glade_xml:
	def __init__(self,file,root=None):
		'''constructor, receives the name of the interface descriptor
		and then initialize gtk.glade.XML'''
		b = Builder(file, root)
		self.xml = b.builder
				
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
	
class Builder:
	def __init__(self, file, root):
		'''
		Load a GUI description from a gtkbuilder file
		'''
		self.__widgets = {}
		locale_dir = os.path.join(DATADIR, 'locale')
		self.builder = gtk.Builder()
		self.builder.add_from_file(file)
		self.builder.set_translation_domain(PROGRAMNAME)
		self.builder.signal_autoconnect = self.builder.connect_signals
		if root:
			widget = self.get_widget(root)
			if not isinstance(widget, gtk.Menu):
				if widget.get_parent():
					parent= widget.get_parent()
					parent.remove(widget)
					widget.unparent()
		self.builder.get_widget = self.get_widget
		widgets = self.builder.get_objects()
		for widget in widgets:
			try:
				self.__widgets[widget.name] = widget
			except AttributeError:
				pass

	
	def get_widget(self, name):
		if not name  in self.__widgets.keys():
			widget = self.builder.get_object(name)
			self.__widgets[name] = widget
			return widget
		widget = self.__widgets[name]
		return widget


class GtkMisc:
	def __init__(self):
		self.__Logger = logging.getLogger('GtkMisc')
		self.wdir = SHARE_PATH

	def gen_pixbuf(self,imagefile):
		'''Create a pixbuf from  a file'''
		pixbuf = self.gen_pixbuf_from_file(os.path.join(self.wdir,imagefile))
		return pixbuf
	
	def gen_pixbuf_from_file(self, filename):
		pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
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
				"[":"%5B",
				"]":"%5D",
				}
		for i in entities.keys():
			text = text.replace(i,entities[i])
		return text
	
	def replace_XML_entities(self,text):
		entities = {"&amp;":"&",
				"&lt;":"<",
				"&gt":">;",
				"%20":" ",
				"%5B":"[",
				"%5D":"]",
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
		for i in ('latin-1','iso8859-1', 'utf8'):
			try:
				text1 = unicode(text, i)
				text1 =  text1.encode(i)
				return text1
			except Exception, e:
				pass
		return text

class CairoMisc:
	def __init__(self):
		self.colors = {}

	def getCairoColor(self, color):
		if color in self.colors.keys():
			return color
		ncolor = color/65535.0
		self.colors[ncolor] = ncolor
		return ncolor

	def hex2float(self, hex):
		if hex in self.hex.keys():
			return self.hex[hex]
		ret = []
		for i in xrange(4):
			ret.append(int(hex[i]) / 255.0)
		self.hex[hex] = ret
		return ret

	def render_rect(self, cr, x, y, w, h, o):
		'''
		create a rectangle with rounded corners
		'''
		x0 = x
		y0 = y
		rect_width = w
		rect_height = h
		radius = 5 + o

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
