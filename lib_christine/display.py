#!/usr/bin/env python

# test for writting a custom gtk-cairo widget


import gtk, cairo, pango, gobject

BORDER_WIDTH = 3
POS_INCREMENT = 3
LINE_WIDTH = 2

class display(gtk.DrawingArea):
	def __init__(self,text=""):
		gtk.DrawingArea.__init__(self)
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

	def set_text(self,text):
		self.__text = text

	def set_song(self,song):
		if type(song) != type(""):
			raise TypeError("Paramether must be text")
		self.__song = song
	
	def __button_press_event(self,widget,event):
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
			#self.set_text("%f"%value)
			self.emit("value-changed",self)
		#print "width:",width
		#print "xy:",x,y
		#print "minx,miny:",minx,miny
		#print "maxx,maxy:",maxx,maxy
		#print "======================"
	def get_value(self):
		return self.__value

	def __motion_notify(self,widget,event):
		return True
	
	def expose_event(self,widget,event):
		x,y,w,h = self.allocation
		self.x,self.y,self.w,self.h = self.allocation

		self.context = self.window.cairo_create()
		self.context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		self.context.clip()

		self.context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		self.context.set_source_rgb(1,1,1)
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
		self.context.rectangle(fh,(BORDER_WIDTH*2)+fh,
				width,BORDER_WIDTH)
		self.context.set_line_width(LINE_WIDTH)
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
		
	def set_scale(self,value):
		try:
			value = float(value)
		except ValueError,a:
			raise ValueError(a)
		if value > 1.0 or value < 0.0:
			raise ValueError("value > 1.0 or value < 0.0")
		self.width = value
		self.emit("expose-event",gtk.gdk.Event(gtk.gdk.EXPOSE))


class window:
	def __init__(self):
		self.window = gtk.Window()
		self.window.set_border_width(10)
		self.window.connect("destroy",gtk.main_quit)
		self.window.set_default_size(1000,0)
		vbox = gtk.VBox(False,2)
		a = test()
		vbox.pack_start(a,False,False,2)
		self.window.add(vbox)
		entry = gtk.Entry()
		entry.connect("changed",lambda widget: a.set_text(widget.get_text()))
		vbox.pack_start(entry,False,False,2)

		adjustment = gtk.Adjustment(0,
								0.0,
								1.0,
								0.01,
								0.2,
								0.2)
		spin = gtk.SpinButton(adjustment,
				0,2)
		spin.connect("changed",lambda widget: a.set_scale(widget.get_value()))
		vbox.pack_start(spin,False,False,2)
		self.window.show_all()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	a = window()
	a.main()
