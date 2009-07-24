#!/usr/bin/env python

import gtk
import sys
import traceback
import webbrowser
from libchristine.Share import Share
from libchristine.Logger import LoggerManager

class BugReport:
	def __init__(self):
		self.logger = LoggerManager('BugReport')
		self.__Share = Share()
		xml = self.__Share.getTemplate('errorReporter')
		vals = '\n'.join([str(k) for k in self.formatExceptionInfo()])
		self.logger.error(vals)
		window = xml['window']
		textview = xml['textview']
		buffer = textview.get_buffer()
		buffer.set_text(vals)
		button = xml['reportButton']
		button.connect('clicked', lambda button: webbrowser.open('http://sourceforge.net/tracker/?group_id=167966'))
		window.show_all()

	def __windowKeyPressHandler(self, window, event):
		if event.keyval == gtk.gdk.keyval_from_name('Escape'):
			window.destroy()

	def formatExceptionInfo(self):
		trbk = sys.exc_info()[2]
		result = traceback.extract_tb(trbk, limit=100)
		return result