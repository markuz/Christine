#!/usr/bin/env python

# test for writting a custom gtk-cairo widget


import gtk, cairo, pango, gobject

BORDER_WIDTH = 3
POS_INCREMENT = 3
LINE_WIDTH = 2

class display(gtk.DrawingArea):
	def __init__(self,text=""):
		'''
		Constructor
		'''
		# since this class inherits methods and properties
		# from gtk.Drawind_area we need to initialize
		# it too.
		gtk.DrawingArea.__init__(self)
		# This flag is supposed to be used to check if the
		# display y being drawed.
		self.__DRAWING = False
		# Adding some events
		self.set_property("events",gtk.gdk.EXPOSURE_MASK|
								gtk.gdk.POINTER_MOTION_MASK|
								gtk.gdk.BUTTON_PRESS_MASK)
		self.connect("button-press-event",self.__button_press_event)
		self.connect("expose-event",self.expose_event)
		gobject.signal_new("value-changed",self,
				gobject.SIGNAL_RUN_LAST,
				gobject.TYPE_NONE,
				(gobject.TYPE_PYOBJECT,))
		self.__song = ""
		self.__text = ""
		self.wpos = 0
		self.width = 0
		self.set_text(text)
		self.set_size_request(300,42)

	def __button_press_event(self,widget,event):
		'''
		Called when a button is pressed in the 
		display
		'''
		x,y = self.get_pointer()
		minx,miny = self._layout.get_pixel_size()
		minx = miny
		width = self.w-miny-(BORDER_WIDTH*3)
		miny = miny+(BORDER_WIDTH*2)
		maxx = minx + width
		maxy = miny + BORDER_WIDTH
		if x >= minx and x <= maxx \
				and y >= miny and y <= maxy:
			value = (x-minx)*1.0/(width)
			self.set_scale(value)
			self.__value = value
			self.emit("value-changed",self)

	#def __motion_notify(self,widget,event):
	#	return True

	def set_text(self,text):
		self.__text = text

	def set_song(self,song):
		if type(song) != type(""):
			raise TypeError("Paramether must be text")
		self.__song = song

	def get_value(self):
		return self.width

	def set_scale(self,value):
		try:
			value = float(value)
		except ValueError,a:
			raise ValueError(a)
		if value > 1.0 or value < 0.0:
			raise ValueError("value > 1.0 or value < 0.0")
		self.width = value
		self.emit("expose-event",gtk.gdk.Event(gtk.gdk.EXPOSE))
	

	def expose_event(self,widget,event):
		'''
		This function is used to draw the display.
		'''
		# Every speed improvement is really appreciated.
		if self.__DRAWING:
			return True
		self.DRAWING = True
		x,y,w,h = self.allocation
		self.x,self.y,self.w,self.h = self.allocation

		self.context = self.window.cairo_create()
		self.context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		self.context.clip()

		self.context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		self.context.set_source_rgba(1,1,1,1)
		self.context.fill_preserve()
		self.context.set_source_rgb(0,0,0)
		self.context.stroke()

		# Write text
		x,y,w,h = self.allocation
		self._layout = self.create_pango_layout(self.__song)
		self._layout.set_font_description(pango.FontDescription("Sans Serif 8"))
		fontw,fonth = self._layout.get_pixel_size()
		self.context.move_to((w-fontw)/2,(fonth)/2)
		self.context.update_layout(self._layout)
		self.context.show_layout(self._layout)

		fw,fh = self._layout.get_pixel_size()
		width = self.w-fh-(BORDER_WIDTH*3)
		self.context.set_antialias(cairo.ANTIALIAS_NONE)
		self.context.rectangle(fh,(BORDER_WIDTH*2)+fh,
				width,BORDER_WIDTH)
		self.context.set_line_width(1)
		self.context.set_line_cap(cairo.LINE_CAP_BUTT)
		self.context.set_source_rgb(0,0,0)
		self.context.stroke()
		
		width = self.width * width
		self.context.rectangle(fh,(BORDER_WIDTH*2)+fh,
				width,BORDER_WIDTH)
		self.context.set_source_rgb(0,0,0)
		self.context.fill_preserve()
		self.context.set_source_rgb(0,0,0)
		self.context.stroke()
		layout = self.create_pango_layout(self.__text)
		fontw,fonth = layout.get_pixel_size()
		self.context.move_to((w-fontw)/2,(fonth+33)/2)
		layout.set_font_description(pango.FontDescription("Sans Serif 8"))
		self.context.update_layout(layout)
		self.context.show_layout(layout)
		self.__DRAWING = False
		
	value = property(get_value,set_scale)
