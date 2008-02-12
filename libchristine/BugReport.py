#!/usr/bin/env python

import gtk
import sys
import traceback
import webbrowser
from libchristine.Share import Share

class BugReport:
	def __init__(self):
		self.__Share = Share()
		xml = self.__Share.getTemplate('errorReporter')
		vals = repr(self.formatExceptionInfo())
		window = xml['window']
		textview = xml['textview']
		buffer = textview.get_buffer()
		buffer.set_text(vals)
		button = xml['reportButton']
		button.connect('clicked', lambda button: webbrowser.open('http://sourceforge.net/tracker/?group_id=167966'))
		window.show()

	def __windowKeyPressHandler(self, window, event):
		if event.keyval == gtk.gdk.keyval_from_name('Escape'):
			window.destroy()

	def formatExceptionInfo(self, maxTBlevel=5):
	 	cla, exc, trbk = sys.exc_info()
		excName = cla.__name__
		try:
			excArgs = exc.__dict__["args"]
		except KeyError:
			excArgs = "<no args>"
		excTb = traceback.format_tb(trbk, maxTBlevel)
		serror = excTb[0].split("\n")
		serror = serror[0].strip()
		return (excName, excArgs, excTb, serror)

