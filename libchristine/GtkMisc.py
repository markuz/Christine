#! /usr/bin/env python
# -*- coding: UTF-8 -*-

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
import gobject
import gconf
import os.path
import gtk.glade
import libchristine.ChristineDefinitions as ChristineDefinitions

class glade_xml:
	def __init__(self,file,root=None):
		'''constructor, receives the name of the interface descriptor 
		and then initialize gtk.glade.XML'''

		gtk.glade.bindtextdomain(ChristineDefinitions.PROGRAM_NAME,
				ChristineDefinitions.LOCALE_DIR)
		gtk.glade.textdomain(ChristineDefinitions.PROGRAM_NAME)
		self.__xml = gtk.glade.XML(file,root,None)
		self.get_widget = self.__xml.get_widget

	def __getitem__(self,widget):
		'''
		returns the widget according to the name of the widget.
		This lets the instance work like a dictionary
		'''
		return self.__xml.get_widget(widget)

	def signal_autoconnect(self,signals):
		'''
		Signal autoconnect wrapper.
		'''
		self.__xml.signal_autoconnect(signals)

class GtkMisc:
	def __init__(self):
		'''
		Constructor
		'''
		self.wdir = os.path.join(ChristineDefinitions.SHARE_PATH,
					"gui","pixmaps")

	def genPixbuf(self,imagefile):
		'''
		Create a pixbuf from  a file
		@param imagefile: Name of the image to be loaded, must
		be in the pixmaps dir from the working directory
		'''
		pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.wdir,imagefile))
		return pixbuf
	
	def setImage(self,widget,filename):
		'''
		Set the image to a widget. Mostly used in 
		gtk.Buttons and gtk.Windows and gtk.Dialogs
		@param widget: The widget where to set the image
		@param filename: The name of the filename to be loaded
		and used to create the gtk.Image to be set in the widget.
		'''
		image = self.Image(filename)
		widget.set_image(image)
		
	def Image(self,filename):
		'''
		Creates a image from a file.
		'''
		image = gtk.Image()
		image.set_from_pixbuf(self.genPixbuf(filename))
		image.show()
		return image

####def set_toolbutton_image(self,widget,filename):
####	image = self.image(filename)
####	widget.set_icon_widget(image)
	
	def stripXmlEntities(self,text):
		'''
		Strip some entities from the text, 
		usefull when you are working with XML or 
		pango markup language.
		@param text: text to be stripped.
		'''
		entities = {"&":"&amp;",}	
		for i in entities.keys():
			text = text.replace(i,entities[i])
		return text
	
class error:
	def __init__(self,text):
		xml = glade_xml(os.path.join(GUI_PATH,"Error.glade"))
		dialog		= xml["dialog"]
		error_label = xml["error"]
		error_label.set_text(text)
		dialog.run()
		dialog.destroy()
