#!/usr/bin/env python

# test for writting a custom gtk-cairo widget


import gtk, cairo, pango, gobject

BORDER_WIDTH = 3
POS_INCREMENT = 3
LINE_WIDTH = 0.5 

class display(gtk.DrawingArea):
	def __init__(self,text=""):
		gtk.DrawingArea.__init__(self)
		#print self.get_property("events").value_nicks
		self.set_property("events",gtk.gdk.EXPOSURE_MASK|
								gtk.gdk.POINTER_MOTION_MASK|
								gtk.gdk.BUTTON_PRESS_MASK)
		self.connect("expose-event",self.expose)
		self.connect("button-press-event",self.__button_press_event)
		#self.connect("motion-notify-event",self.__motion_notify)
		self.__song = ""
		self.__text = ""
		self.wpos = 0
		self.width = 0
		self.set_text(text)
		#fontw,fonth = self._layout.get_pixel_size()
		self.set_size_request(300,42)
		#gobject.timeout_add(200,self.__motion_notify)
	
	def set_text(self,text):
		self.__text = text

	def set_song(self,song):
		if type(song) != type(""):
			raise TypeError("Paramether must be text")
		self.__song = song
	
	def __button_press_event(self,widget,event):
		x,y = self.get_pointer()
		#width = self.width * width
		minx,miny = self._layout.get_pixel_size()
		minx = miny
		width = self.w-miny-(BORDER_WIDTH*3)
		miny = miny+(BORDER_WIDTH*2)
		maxx = minx + width
		maxy = miny + BORDER_WIDTH
		if x >= minx and x <= maxx \
				and y >= miny and y <= maxy:
			value = (x-minx)*1.0/(width)
			print value,maxx -minx
			self.set_scale(value)
			self.set_text("%f"%value)
		print "withh:",width
		print "xy:",x,y
		print "minx,miny:",minx,miny
		print "maxx,maxy:",maxx,maxy
		print "======================"

	

	def __motion_notify(self,widget,event):
		print self.get_pointer()
		return True
	
	def expose(self,widget,event):
		try:
			self.area = event.area
		except:
			pass
		self.create_context()
		self.draw(self.context)
		return False

	
	def create_context(self):
		self.context = self.window.cairo_create()
		(self.x,
		self.y,
		self.w,
		self.h) = self.area
		self.context.rectangle(BORDER_WIDTH, 
							BORDER_WIDTH,
							self.area.width -2*BORDER_WIDTH, 
							self.area.height -2*BORDER_WIDTH)
		self.context.clip()
	
	def draw(self,context):
		rect = self.get_allocation()
		x = rect.x
		y = rect.y
		w = rect.width 
		h = rect.height 
		context.rectangle(BORDER_WIDTH,BORDER_WIDTH,
				w -2*BORDER_WIDTH,h - 2*BORDER_WIDTH)
		context.set_source_rgb(1,1,1)
		context.fill_preserve()
		context.set_source_rgb(0,0,0)
		context.stroke()

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
		#print width,self.w,fh
		context.rectangle(fh,(BORDER_WIDTH*2)+fh,
				width,BORDER_WIDTH)
		context.set_line_width(LINE_WIDTH)
		context.set_source_rgb(0,0,0)
		context.stroke()
		
		width = self.width * width
		context.rectangle(fh,(BORDER_WIDTH*2)+fh,
				width,BORDER_WIDTH)
		context.set_source_rgb(0,0,0)
		context.fill_preserve()
		context.set_source_rgb(0,0,0)
		context.stroke()
		
		layout = self.create_pango_layout(self.__text)
		x,y,w,h = self.allocation
		fontw,fonth = layout.get_pixel_size()
		self.context.move_to((w-fontw)/2,(fonth+33)/2)
		layout.set_font_description(pango.FontDescription("Sans Serif 8"))
		self.context.update_layout(layout)
		self.context.show_layout(layout)




		
	def write_text(self):
		x,y,w,h = self.allocation
		fontw,fonth = self._layout.get_pixel_size()
		self.context.move_to((w-fontw)/2,(fonth)/2)
		self._layout = self.create_pango_layout(self.__text)
		self._layout.set_font_description(pango.FontDescription("Sans Serif 8"))
		self.context.update_layout(self._layout)
		self.context.show_layout(self._layout)

	def move_text(self):
		if self.wpos > self.allocation.width:
			self.wpos = 0
		self.wpos += POS_INCREMENT
		#print self.wpos,self.allocation.width
		self.create_context()
		self.draw(self.context)
		return True

	def set_scale(self,value):
		try:
			value = float(value)
		except ValueError,a:
			raise ValueError(a)
		if value > 1.0 or value < 0.0:
			raise ValueError("value > 1.0 or value < 0.0")
		self.width = value
		self.create_context()
		self.draw(self.context)


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
