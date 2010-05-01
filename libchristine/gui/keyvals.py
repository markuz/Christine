#python
#Valores para las teclas de acuerdo a Gtk.

import gtk

UP = gtk.gdk.keyval_from_name('Up')
DOWN = gtk.gdk.keyval_from_name('Down')
LEFT = gtk.gdk.keyval_from_name('Left')
RIGHT = gtk.gdk.keyval_from_name('Right')
ENTER = gtk.gdk.keyval_from_name('Return')
INTRO = gtk.gdk.keyval_from_name('KP_Enter')
TAB = gtk.gdk.keyval_from_name('Tab')
BACKSPACE = gtk.gdk.keyval_from_name('BackSpace')
DELETE = gtk.gdk.keyval_from_name('Delete')
PERIOD = gtk.gdk.keyval_from_name('period')
KP_DECIMAL = gtk.gdk.keyval_from_name('KP_Decimal')
KP_ADD = gtk.gdk.keyval_from_name('KP_Add')
PLUS  = gtk.gdk.keyval_from_name('plus')
KP_SUBSTRACT = gtk.gdk.keyval_from_name('KP_Subtract')
KP_DIVIDE = gtk.gdk.keyval_from_name('KP_Divide')
KP_MULTIPLY = gtk.gdk.keyval_from_name('KP_Multiply')
ASTERISK = gtk.gdk.keyval_from_name('asterisk')
ESCAPE = gtk.gdk.keyval_from_name('Escape')
PAGEUP = gtk.gdk.keyval_from_name('Page_Down')
PAGEDOWN = gtk.gdk.keyval_from_name('Page_Up')

NUMBERS = []
for i in tuple('1234567890'):
	for j in ('','KP_'):
		NUMBERS.append(gtk.gdk.keyval_from_name(j+i))

DOTS = (PERIOD, KP_DECIMAL)
DELETES = ( BACKSPACE, DELETE )
ADDS = (PLUS, KP_ADD)