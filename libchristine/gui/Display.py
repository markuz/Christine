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
import time

import gtk
import pangocairo
import cairo
import gobject
import math
from libchristine.Validator import *
from libchristine.gui.GtkMisc import CairoMisc, GtkMisc
from libchristine.Events import christineEvents
from libchristine.Share import Share
from libchristine.christineConf import christineConf

BORDER_WIDTH  = 3
POS_INCREMENT = 3
LINE_WIDTH    = 2

class Display(gtk.DrawingArea, CairoMisc, GtkMisc):#, object):
    """
    Display the track progress in christine
    """
    __gsignals__ = {
                'value-changed':(
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    }
    

    def __init__(self, text= ''):
        """
        Constructor
        """
        # since this class inherits methods and properties
        # from gtk.Drawind_area we need to initialize it too
        gtk.DrawingArea.__init__(self)
        CairoMisc.__init__(self)
        GtkMisc.__init__(self)
        self.share = Share()
        self.config = christineConf()
        self.display = self
        self.__ButtonPress = False
        self.__last_time_moved = time.time()
        self.__last_emit = time.time()
        self.__override_timer = False
        self.Events = christineEvents()
        self.__color1 = gtk.gdk.color_parse('#FFFFFF')
        self.__color2 = gtk.gdk.color_parse('#3D3D3D')
        # Adding some events
        self.set_property('events', gtk.gdk.EXPOSURE_MASK |
                                    gtk.gdk.POINTER_MOTION_MASK |
                                    gtk.gdk.BUTTON_PRESS_MASK|
                                    gtk.gdk.BUTTON_RELEASE_MASK|
                                    gtk.gdk.ENTER_NOTIFY_MASK|
                                    gtk.gdk.LEAVE_NOTIFY_MASK)
        self.connect('expose-event',       self.__do_expose)
        self.connect('button-press-event', self.__buttonPressEvent)
        self.connect('button-release-event', self.__buttonReleaseEvent)
        self.connect('configure-event', self.__on_size_allocate)
        self.connect('motion-notify-event', self.__motion_notify)
        self.connect('leave-notify-event', self.__leave_notify)
        #self.connect('size-allocate', self.__size_allocate)

        self.__Song           = ""
        self.__Text           = ""
        self.__WindowPosition = 0
        self.__Value          = 0
        self.setText(text)
        self.set_size_request(100, 30)
        self.Events.addWatcher('gotTags', self.gotTags)
        gobject.timeout_add(1000, self.__emit)

        self.__shuffle_pixbuf = self.scalePixbuf(self.share.getImageFromPix('usort'), 16,16)
        self.__non_shuffle_pixbuf = self.scalePixbuf(self.share.getImageFromPix('sort'),16,16)
        self.__repeat_pixbuf = self.scalePixbuf(self.share.getImageFromPix('repeat'), 16,16)
        self.__non_repeat_pixbuf = self.scalePixbuf(self.share.getImageFromPix('urepeat'),16,16)
        self.value = 0

    
    def __size_allocate(self,display, area):
        x,y,w,h = area
        self.set_size_request(w,h)
        
    
    def gotTags(self, tags):
        tooltext = tags['title']
        if (tags['artist'] != ''):
            tooltext    += " by %s" % tags['artist']
        if (tags['album'] != ''):
            tooltext    +=  " from %s" % tags['album']
        if tooltext:
            self.tooltext = tooltext
            self.setSong(tooltext)
        
    def __motion_notify(self, widget, event):
        mx,my = self.get_pointer()
        x,y,w,h = self.allocation
        if mx > x and mx < w and my > y and my < h:
            if time.time() - self.__last_time_moved > 0.05:
                self.__override_timer = True
                self.__emit()
                self.__override_timer = False
                self.__last_time_moved = time.time()
        
    def __leave_notify(self, widget,event):
        self.__ButtonPress = False
            
    def __emit(self):
        '''
        Emits an expose event
        '''
        self.emit('expose-event', gtk.gdk.Event(gtk.gdk.EXPOSE))
        return True

    def __buttonPressEvent(self, widget, event):
        self.__ButtonPress = True
        
    def __buttonReleaseEvent(self, widget, event):
        """
        Called when a button is pressed in the display
        """
        self.__ButtonPress = False
        (nx,ny, w, h)   = self.allocation
        (x, y)       = self.get_pointer()
        (minx, miny) = self.__Layout.get_pixel_size()
        minx         = miny
        width        = (w - miny - (BORDER_WIDTH * 3))
        miny         = (miny + (BORDER_WIDTH * 2))
        maxx         = (minx + width)
        maxy         = (miny + BORDER_WIDTH)
        cond_to_pbar = (x > minx and x <= w ) and (y >=miny and y <= h)
        if cond_to_pbar :
            value = (((x - minx) * 1.0) / width)
            if value <0:
                value = 0
            self.setScale(value)
            self.emit("value-changed",self)
            return
        cond_to_shuffle = (x >= 10 and x <= 26) and (y >= 3 and y <= 19)
        cond_to_repeat = (x >= 26 and x <= 38) and (y >= 3 and y <= 19)
        if cond_to_shuffle:
            self.config.setValue('control/shuffle',not self.config.get_value('control/shuffle'))
            self.__emit()
        elif cond_to_repeat:
            self.config.setValue('control/repeat',not self.config.get_value('control/repeat'))
            self.__emit()


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
        self.__Song = self.encode_text(song)
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
    
    def __do_expose(self,widget,event):
        if getattr(self,'window', None) == None:
            return False
        x,y,w,h = self.allocation
        x,y = (0,0)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w,h)
        context = cairo.Context(surface)
        context.move_to(0, 0)
        #context.set_line_width(1.5)
        self.render_rect(context, x, y, w, h, 0.5)
        context.clip_preserve()
        context.save()
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()
        context.restore()
        
        tcolor = self.style.fg[0]
        wcolor = self.style.bg[0]
        bcolor = gtk.gdk.color_parse("#000000")
        b1color = gtk.gdk.color_parse("grey")
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
        
        self.render_rect(context, x, y, w, h, 0.5)
        
        linear = cairo.LinearGradient(x+1, y+1 , x+1, h-1)
        color = gtk.gdk.color_parse("#F8FBE2")
        cr, cg,cb = map(self.getCairoColor, (color.red, color.green, color.blue))
        colorbg = gtk.gdk.color_parse("#D6D0B7")
        cr1, cg1,cb1 = map(self.getCairoColor, (colorbg.red, colorbg.green, colorbg.blue))
        linear.add_color_stop_rgb(0.0,cr,cg,cb,)
        linear.add_color_stop_rgb(0.5,cr1,cg1,cb1)
        linear.add_color_stop_rgb(1.0,cr,cg,cb,)
        context.set_source(linear)
        context.fill_preserve()

        #Greadiente para el borde
        color = gtk.gdk.color_parse("#666")
        cr, cg,cb = map(self.getCairoColor, (color.red, color.green, color.blue))
        context.set_source_rgb(cr, cg, cb)
        context.stroke()
        
        self.draw_text(context, x,y,w,h)
        self.draw_progress_bar(context)
        self.draw_pos_circle(context)
        cr = self.window.cairo_create()
        cr.set_source_surface(surface)
        cr.paint()
        self.show_shuffle()
        self.show_repeat()
        return True
        
    
    def draw_progress_bar(self, context):
        x,y,w,h = self.allocation
        fh = self.__Layout.get_pixel_size()[1]
        width    = ((w - fh) - (BORDER_WIDTH * 3))
        x,y = (0,0)
        # Drawing the progress bar
        self.render_rect(context,fh, ((BORDER_WIDTH * 2) + fh) +1.5 ,
                width, BORDER_WIDTH +1, 3,0)
        #context.rectangle(fh, ((BORDER_WIDTH * 2) + fh) +1.5,
        #        width, BORDER_WIDTH+1)
        context.set_line_width(1)
        context.set_line_cap(cairo.LINE_CAP_BUTT)
        color = gtk.gdk.color_parse("#ddd")
        cr, cg,cb = map(self.getCairoColor, 
                (color.red, color.green, color.blue))
        context.set_source_rgb(cr, cg, cb)
        context.fill_preserve()
        color = gtk.gdk.color_parse("#666")
        cr, cg,cb = map(self.getCairoColor, 
                (color.red, color.green, color.blue))
        context.set_source_rgb(cr, cg, cb)
        context.stroke()
        width = (self.__Value * width)
        self.render_rect(context,fh-1, ((BORDER_WIDTH * 2) + fh)+1, 
                width, BORDER_WIDTH+1,2,0)
        #context.rectangle(fh-1, ((BORDER_WIDTH * 2) + fh)+1, 
        #        width, BORDER_WIDTH+1)
        pat = cairo.LinearGradient(fh, ((BORDER_WIDTH * 2) + fh)+1.5, 
                fh,((BORDER_WIDTH * 2) + fh)+1.5 + BORDER_WIDTH)
        pat.add_color_stop_rgb(0.0, self.bar1 ,self.bag1,self.bab1)
        pat.add_color_stop_rgb(0.9,cr,cg,cb)
        context.set_source(pat)
        context.fill()
    
    def draw_pos_circle(self, context):
        if not self.window:
            return True
        w,h = (self.allocation.width, self.allocation.height)
        x,y = (0,0)
        fh = self.__Layout.get_pixel_size()[1]
        mx,my = self.get_pointer()
        twidth = ((w - fh) - (BORDER_WIDTH * 3))
        if self.__ButtonPress and mx > x and mx < w and my > y and my < h:
            width = mx - fh
            if width > twidth:
                width = twidth
        else:
            width = twidth
            width = (self.__Value * width)
        
        context.set_source_rgb(self.bar,self.bag,self.bab)
        context.set_antialias(cairo.ANTIALIAS_DEFAULT)
        context.arc(int (fh + width),
                (BORDER_WIDTH * 2) + fh + (BORDER_WIDTH/2) +2, 
                4, 
                0, 
                2 * math.pi)
        context.fill_preserve()
        pat = cairo.LinearGradient(    
                fh, 
                (BORDER_WIDTH * 2) + fh + (BORDER_WIDTH/2) +2, 
                fh, 
                (BORDER_WIDTH * 2) + fh + (BORDER_WIDTH/2) +4,
                )
        pat.add_color_stop_rgb(0.0, self.bar1 ,self.bag1,self.bab1)
        pat.add_color_stop_rgb(0.1,self.bar,self.bag,self.bab)
        context.set_source(pat)
        context.fill()
        context.arc(int (fh + width),
                (BORDER_WIDTH * 2) + 
                fh + (BORDER_WIDTH/2) +2, 
                2, 
                0, 
                2 * math.pi)
        context.set_source_rgb(1,1,1)
        context.fill()
    
    def draw_text(self, context, x, y, w , h):
        # Write text
        msg = ''
        if self.__Song:
            msg += self.__Song
        if self.__Text:
            msg += '--' + self.__Text
        self.__Layout  = self.create_pango_layout(msg)
        self.__Layout.set_font_description(self.style.font_desc)
        (fontw, fonth) = self.__Layout.get_pixel_size()
        if self.__HPos == x or fontw < w:
            self.__HPos = (w - fontw) / 2
        elif self.__HPos > (fontw-(fontw*2)):
            self.__HPos = self.__HPos - 1
        else:
            self.__HPos = w + 1
        c = pangocairo.CairoContext(context)
        c.move_to(self.__HPos, (fonth)/2)
        c.set_source_rgb(self.bar,self.bag,self.bab)
        color = gtk.gdk.color_parse("#666")
        cr, cg,cb = map(self.getCairoColor, (color.red, color.green, color.blue))
        context.set_source_rgb(cr, cg, cb)
        c.update_layout(self.__Layout)
        c.show_layout(self.__Layout)
    
    def show_shuffle(self):
        '''
        Show a widget that represent if the current playlist method is
        shuffle or not.
        '''
        if self.config.get_value('control/shuffle'):
            pixbuf = self.__shuffle_pixbuf
        else:
            pixbuf = self.__non_shuffle_pixbuf
        cr = self.window.cairo_create()
        cr.set_source_pixbuf(pixbuf, 10,3 )
        cr.paint()
    
    def show_repeat(self):
        '''
        Show a widget that represent if the current playlist has to 
        be repeated when it ends.
        '''
        if self.config.get_value('control/repeat'):
            pixbuf = self.__repeat_pixbuf
        else:
            pixbuf = self.__non_repeat_pixbuf
        cr = self.window.cairo_create()
        cr.set_source_pixbuf(pixbuf, 26, 3)
        cr.paint()

    value = property(getValue, setScale)
