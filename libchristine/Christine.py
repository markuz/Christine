#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2009 Marco Antonio Islas Cruz
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
# @category  Multimedia
# @package   Christine
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import sys
from random import randint
import time
import gtk
#import gtk.gdk
import gst.interfaces
import gobject
import os
import signal
from libchristine.globalvars import  BUGURL,PIDFILE,TRANSLATEURL
from libchristine.sanity import sanity
sanity()
#from  libchristine.Plugins import Manager
from libchristine.Translator import translate
from libchristine.gui.GtkMisc import GtkMisc, error, load_rc
from libchristine.ui import interface
from libchristine.Library import PATH, HAVE_TAGS
from libchristine.Library import PIX,TIME
#from libchristine.Player import Player
from libchristine.Share import Share
from libchristine.sources_list import LIST_NAME, LIST_TYPE, LIST_EXTRA
from libchristine.Logger import LoggerManager
from libchristine.Events import christineEvents
from libchristine.gui.buttons import next_button, toggle_button, prev_button
try:
	from libchristine.christine_dbus import christineDBus
except Exception, e:
	pass
from libchristine.options import options
#rom libchristine.gui.BugReport import BugReport
#from libchristine.gui.Volume import Volume
import webbrowser
from libchristine.ChristineCore import ChristineCore
from libchristine.gui.mainWindow import mainWindow
from libchristine.gui.keyvals import PAGEDOWN,PAGEUP
from libchristine.gui.equalizer import equalizer

core = ChristineCore()

opts = options()

def close(*args):
	if os.path.exists(PIDFILE):
		os.unlink(PIDFILE)
	sys.exit()
	gtk.main_quit()

def clean_traceback():
	sys.exc_traceback = None
	gc.collect(2)
	return True

#gobject.timeout_add(10000, clean_traceback)

signal.signal(signal.SIGTERM, close)

if (gtk.gtk_version < (2, 16, 0)):
	sys.stderr.write(translate('Gtk+ 2.16 or better is required'))
	sys.exit()

share = Share()
logo = share.getImageFromPix('christine')
gtk.window_set_default_icon(logo)


def gc_collect():
	try:
		gc.collect()
	except:
		pass
	return True

gobject.timeout_add(1000, gc_collect)

if os.name == 'nt':
	load_rc()

class Christine(GtkMisc):
	'''
	Wrapper
	'''
	def __init__(self):
		if opts.options.use_new_main_window:
			c = mainWindow()
		else:
			c = Christine_old()
	
	def runGtk(self):
		gtk.main()

class Christine_old(GtkMisc):
	def __init__(self):
		"""
		Constructor, this method will init the gtk_misc parent class,
		create the XML interface descriptor,
		initialize class variables and create some timeouts calls
		"""
		self.__Logger = LoggerManager().getLogger('Christine')
		GtkMisc.__init__(self)

		self.share   = Share()
		self.christineConf   = core.config
		self.interface = interface()
		self.interface.coreClass = self
		self.interface.config = self.christineConf
		self.Events = christineEvents()

		# Class variables
		self.__ErrorStreamCount = 0
		self.__TimeTotal        = 0     # Nanosecs for audio/video file
		self.__LocationCount    = 0     # Count ns and jump if the file is not good
		self.__LastPlayed       = []
		self.__IterNatural      = None
		self.__ScaleMoving      = False
		self.__IsFullScreen     = False
		self.__ShowButtons      = False
		self.__IsHidden         = False
		self.__LastTags			= []
		self.__lastTypeTime		= time.time()
		self.__StatePlaying = False

		# Create the try icon.
		self.christineConf.notifyAdd('ui/show_in_notification_area',
				lambda cl,cnx,entry,widget: \
				self.interface.TrayIcon.TrayIcon.set_visible(entry.get_value().get_bool()))

		gobject.timeout_add(1000, self.checkTimeOnMedia)
		# Creating the player and build the GUI interface
		self.__buildInterface()
		self.coreWindow.show()
		self.HBoxSearch.hide()
		#plugins_manager = Manager()
		if opts.options.quit:
			sys.exit(0)

	def changeVolumeWithScroll(self,widget,event):
		if event.type == gtk.gdk.SCROLL:
			value = self.__HScaleVolume.get_value()
			diff = 0.05
			if event.direction == gtk.gdk.SCROLL_DOWN:
				value -= diff
			elif event.direction == gtk.gdk.SCROLL_UP:
				value += diff
			if value < 0:
				value = 0.0
			elif  value >1:
				value = 1.0
			self.__HScaleVolume.set_value(value)
			return True
		return False

	def __buildInterface(self):
		"""
		This method calls most of the common used
		interface descriptors (widgets) from xml.
		Connects them to a callback (if needed) and
		call some other methods to show/hide them.
		"""
		xml = self.share.getTemplate('WindowCore')
		xml.signal_autoconnect(self)

		self.__MenuItemSmallView = xml['ViewSmallMenuItem']
		self.__VBoxCore          = xml['VBoxCore']
		self.__VBoxCore.set_property('events',gtk.gdk.ENTER_NOTIFY|
									gtk.gdk.SCROLL_MASK)
		self.__VBoxCore.connect('scroll-event',self.changeVolumeWithScroll)
		self.mainSpace = xml['mainSpace']
		self.mainSpace.add1(core.Player)
		core.Player.connect('gst-error', self.do_gst_error)
		core.Player.connect('end-of-stream', self.do_end_of_stream)
		core.Player.connect('found-tag', self.do_message_tag)
		core.Player.connect('buffering', self.do_buffering)
		#core.Player.bus.add_watch(self.__handlerMessage)

	
		# Calling some widget descriptors with no callback connected "by hand"
		# This interface should not be private.
		#===================================================
		# Public Widgets
		self.MenuBar        = xml['MenuBar']
		self.HBoxSearch    = xml['HBoxSearch']
		self.EntrySearch    = xml['EntrySearch']
		self.EntrySearch.connect('changed',self.search)
		self.EntrySearch.connect('focus-out-event', self.__EntrySearchFocusHandler)
		self.VBoxList       = xml['VBoxList']
		self.HPanedListsBox = xml['HPanedListsBox']

		# Gets window widget from glade template
		self.coreWindow = xml['WindowCore']
		# Uncoment next lines if you want to use RGBA in your theme
		width = self.christineConf.getInt('ui/width')
		height = self.christineConf.getInt('ui/height')
		if not width or not  height:
			width, height = (800,600)
		self.coreWindow.set_default_size(width, height)
		self.coreWindow.connect("destroy",lambda widget: widget.hide())
		self.coreWindow.connect("scroll-event",self.changeVolumeWithScroll)
		self.coreWindow.connect('size-allocate', self.__on_corewindow_resized)
		self.interface.coreWindow = self.coreWindow

		self.__HBoxButtonBox		= xml['HBoxButtonBox']
		self.__HBoxButtonBox.set_property('events',gtk.gdk.ENTER_NOTIFY|gtk.gdk.SCROLL_MASK)
		self.__HBoxButtonBox.connect('scroll-event',self.changeVolumeWithScroll)

		parent = self.__HBoxButtonBox
		prev1 = prev_button()
		parent.pack_start(prev1, False, False, 2)
		prev1.connect('clicked', self.goPrev)
		prev1.show()


		self.PlayButton = toggle_button("")
		self.PlayButton.connect('toggled', self.switchPlay)
		parent.pack_start(self.PlayButton, False, False, 2)
		self.PlayButton.show()
		self.interface.playButton =  self.PlayButton
		self.menuItemPlay = xml['MenuItemPlay']
		
		next = next_button()
		parent.pack_start(next, False, False, 2)
		next.connect('clicked', self.goNext)
		next.show()

		openremotemitem = xml['open_remote1']
		openremotemitem.connect('activate', self.openRemote)
		self.Menus = {}
		for i in ('media', 'edit', 'control', 'help'):
			self.Menus["%s" % i] = xml["%s_menu" % i].get_submenu()

		self.__HBoxCairoDisplay = xml['HBoxCairoDisplay']

		# Create the display and attach it to the main window
		core.Display.connect('value-changed', self.onScaleChanged)
		#self.__HBoxCairoDisplay.pack_start(core.Display, True, True, 0)
		self.__HBoxCairoDisplay.add(core.Display)
		self.__HBoxCairoDisplay.set_expand(True)
		core.Display.show()

		# Create the library by calling to libs_christine.library class
		lastSourceUsed = self.christineConf.get('backend/last_source')
		if not lastSourceUsed:
			lastSourceUsed = 'music'
		core.mainLibrary.loadLibrary(lastSourceUsed)
		core.mainLibrary.tv.show()

		core.mainLibrary.scroll
		#self.libraryVBox = xml['libraryVBox']
		self.mainSpace.add2(core.mainLibrary.scroll)
		core.mainLibrary.show_all()
		core.Player.hide()
		
		self.__VBoxList = xml["VBoxList"]
		self.sideNotebook = gtk.Notebook()
		self.sideNotebook.set_show_tabs(False)
		self.sideNotebook.show_all()
		self.__VBoxList.pack_start(self.sideNotebook, True, True, 0)


		label = gtk.Label(_('Queue'))
		label.set_angle(90)
		self.sideNotebook.append_page(core.Queue.scroll, label)
		#self.VBoxList.pack_start(core.Queue.scroll, False, False, 0)
		self.Queue_mi = xml['Queue']
		self.Queue_mi.connect('activate', lambda x: self.sideNotebook.set_current_page(0))
		core.Queue.tv.connect('row-activated',   core.Queue.itemActivated)
		core.Queue.connect('size-changed',   self.__check_queue)

		label = gtk.Label(_('Sources List'))
		label.set_angle(90)
		self.sources_mi = xml['SourcesList']
		self.sources_mi.connect('activate', lambda x: self.sideNotebook.set_current_page(1))
		self.sideNotebook.append_page(core.sourcesList.vbox, label)
		#self.VBoxList.pack_start(core.sourcesList.vbox)
		core.sourcesList.treeview.connect('row-activated',
				self.__srcListRowActivated)
		core.sourcesList.vbox.show_all()
		self.__ControlButton = xml['control_button']
		self.__MenuItemShuffle = xml['MenuItemShuffle']
		self.__MenuItemShuffle.set_active(self.christineConf.getBool('control/shuffle'))
		self.__MenuItemShuffle.connect('toggled',
			lambda widget: self.christineConf.setValue('control/shuffle',
			widget.get_active()))

		self.christineConf.notifyAdd('control/shuffle',
			self.christineConf.toggleWidget,
			self.__MenuItemShuffle)

		self.__ControlRepeat = xml['repeat']
		self.__ControlRepeat.set_active(self.christineConf.getBool('control/repeat'))

		self.__ControlRepeat.connect('toggled',
			lambda widget: self.christineConf.setValue('control/repeat',
			widget.get_active()))

		self.christineConf.notifyAdd('control/repeat',
			self.christineConf.toggleWidget,
			self.__ControlRepeat)
		
		self.__MenuItemVisualMode = xml['MenuItemVisualMode']
		self.__MenuItemVisualMode.set_active(self.christineConf.getBool('ui/visualization'))

		self.visualModePlayer()

		self.__MenuItemSmallView.set_active(self.christineConf.getBool('ui/small_view'))
		self.toggleViewSmall(self.__MenuItemSmallView)
		
		self.MenuItemSidePane = xml ['sidepanel']
		self.MenuItemSidePane.connect('toggled', self.ShowHideSidePanel)
		self.MenuItemSidePane.set_active(self.christineConf.getBool('ui/sidepanel'))
		self.christineConf.notifyAdd('ui/sidepanel',
									self.christineConf.toggleWidget,
									self.MenuItemSidePane)
		
		translateMenuItem = xml['translateThisApp']
		translateMenuItem.connect('activate', 
				lambda widget: webbrowser.open(TRANSLATEURL))

		reportaBug = xml['reportABug']
		reportaBug.connect('activate', lambda widget: webbrowser.open(BUGURL))


		self.__HScaleVolume         = xml['HScaleVolume']
		self.__HScaleVolume.connect("scroll-event",self.changeVolumeWithScroll)

		volume = self.christineConf.getFloat('control/volume')
		if (volume):
			self.__HScaleVolume.set_value(volume)
		else:
			self.__HScaleVolume.set_value(0.8)

		self.jumpToPlaying(location = self.christineConf.getString('backend/last_played'))
		self.__pidginMessage = self.christineConf.getString('pidgin/message')
		gobject.timeout_add(1000, self.__check_items_on_media)

		self.VBoxList2 = xml["VBoxList2"]
		self.eq = equalizer()
		self.eq.connect('close', lambda x: self.hide_equalizer())
		self.infoBar = gtk.InfoBar()
		self.infoBar.get_content_area().pack_start(self.eq.topWidget)
		self.equalizer_mi = xml["equalizer_mi"]
		self.equalizer_mi.connect('activate', lambda x: self.infoBar.show_all())
		self.VBoxList2.pack_start(self.infoBar,False, False, 2)
		self.VBoxList2.show()
		self.hide_equalizer()
		#eq.topWidget.show_all()
	
	def hide_equalizer(self):
		if not getattr(self, 'infoBar', False):
			return
		self.infoBar.hide()
		
	
	def __check_queue(self, queue, size):
		if size < 1:
			self.sources_mi.activate()
		else:
			self.Queue_mi.activate()
		
	
	def __check_items_on_media(self):
		size = len(core.mainLibrary.model.basemodel)
		if size>1:
			randompath = (randint(1,size-1),)
		else:
			randompath = (0,)
		if randompath[0]:
			filepath, tags = core.mainLibrary.model.basemodel.get(
							core.mainLibrary.model.basemodel.get_iter(randompath),
							PATH,HAVE_TAGS)
			if not tags:
				core.mainLibrary.check_single_file_data(filepath)
		return True

	def __srcListRowActivated(self, treeview, path, column):
		model = treeview.get_model()
		fname, ftype, fextra = model.get(model.get_iter(path), LIST_NAME, LIST_TYPE, LIST_EXTRA)
		if ftype == 'source':
			if fname == 'Library':
				return True
			core.mainLibrary.loadLibrary(fname)
			self.christineConf.setValue('backend/last_source', fname)
		elif ftype == "radio":
			if fname == 'Radio':
				return True
			location = fextra['url']
			extension = location.split(".").pop()
			if location.split(":")[0] == "file" or \
				location[0] == '/':
				if location.split(":")[0] == "file":
					file = ":".join(location.split(":")[1:])[2:]
				else:
					file = location
				try:
					urldesc = open(file)
				except IOError:
					error(translate('%s does not exists'%file))
					return False
			else:
				if os.name == 'posix':
					import urllib
					gate = urllib.FancyURLopener()
					urldesc = gate.open(location)
				else:
					urldes = location

			if extension == "pls":
				for i in urldesc.readlines():
					if i.lower().find("file") >= 0:
						location = i.split("=").pop().strip()
						break
			self.setLocation(location.strip().strip("'"))
			self.simplePlay()
	
	def __on_corewindow_resized(self, window, event):
		'''
		This method is called every time the main window is resized
		'''
		width,height = window.get_size()
		self.christineConf.setValue('ui/width',width)
		self.christineConf.setValue('ui/height',height)

	def setLocation(self, filename):
		"""
		Set the location in the player and
		perform some other required actions
		"""
		self.__StatePlaying = False
		self.__IterNatural  = None
		# current iter is a temporal variable
		# that will hold a gtk.TreeIter
		# should be setted to None
		# before using it

		core.Player.stop()
		core.Player.setLocation(filename)
		name = os.path.split(filename)[-1]
		core.Display.setSong(name)
		self.__LastPlayed.append(filename)
		# enable the stream-length for the current song.
		# this will be stopped when we get the length
		gobject.timeout_add(500,self.__streamLength)
		# if we can't get the length, in more than 20
		# times in the same song, then, jump to the
		# next song
		if (self.__LocationCount > 20):
			gobject.timeout_add(1000, self.goNext)
			self.__LocationCount = 0
		else:
			self.__LocationCount +=1
		core.mainLibrary.tv.grab_focus()
		if core.Player.getType() == 'video':
			self.__MenuItemVisualMode.set_active(False)
			gobject.idle_add(self.__MenuItemVisualMode.set_active,True)

	def stop(self, widget=None):
		"""
		Stop the player
		"""
		core.Player.stop()

	def changeVolume(self, widget):
		"""
		Callback for the volume scale widget
		"""
		value = widget.get_value()
		core.Player.setVolume(value)
		self.christineConf.setValue('control/volume', value)

	def toggleViewSmall(self, widget):
		"""
		Toggle between the small and the large view
		"""
		#
		# The need to use the "self.coreWindow.get_size()" will be
		# erased in the future, window size will be saved in
		# gconf.
		#
		active = widget.get_active()
		self.christineConf.setValue('ui/small_view', active)

		if (active):
			self.HPanedListsBox.hide()
			self.HBoxSearch.hide()

			self.coreWindowSize = self.coreWindow.get_size()
			self.coreWindow.unmaximize()
			self.coreWindow.resize(10, 10)
			self.coreWindow.set_resizable(False)
		else:
			try:
				(w, h) = self.coreWindowSize
			except:
				w = self.christineConf.getInt('ui/width')
				h = self.christineConf.getInt('ui/height')


			self.HPanedListsBox.show()
			self.HBoxSearch.show()
			if w < 1:
				w = 100
			if h < 1:
				h =  100
			self.coreWindow.resize(w, h)
			self.coreWindow.set_resizable(True)

	def toggleVisualization(self, widget):
		"""
		This show/hide the visualization
		"""
		self.christineConf.setValue('ui/visualization', widget.get_active())
		self.visualModePlayer()

		# Be shure that we are not in small view mode.

		if ((self.__MenuItemSmallView.get_active()) and (not widget.get_active())):
			self.toggleViewSmall(self.__MenuItemSmallView)
		core.Player.setVisualization(widget.get_active())
		core.Player.set_property('visible', core.Player.isVideo() or \
				self.christineConf.getBool('ui/visualization'))

	def toggleFullScreen(self, widget = None):
		"""
		Set the full Screen mode
		"""
		#Set the player visualization
		# Only if we are not in FullScreen and we are playing a video.
		if not self.__IsFullScreen:
			self.__IsFullScreen = True
			self.coreWindow.fullscreen()
			if core.Player.isVideo() or self.christineConf.getBool('ui/visualization'):
				self.__VBoxList.set_size_request(0,0)
		else:
		# Non-full screen mode.
		# hide if we are not playing a video nor
		# visualization.
			if not core.Player.isVideo() and \
					not self.christineConf.getBool('ui/visualization'):
				core.Player.hide()
			core.mainLibrary.scroll.set_size_request(200,200)
			self.__VBoxList.set_size_request(150,0)

			self.coreWindow.unfullscreen()
			self.__IsFullScreen = False

	def viewPlayButtons(self, widget = None):
		"""
		This show/hide the player buttons. Suppossed to work only on
		fullscreen mode
		"""
		if (not self.__IsFullScreen):
			return True

		if (self.__ShowButtons):
			#self.__HBoxToolBoxContainer.show()
			self.MenuBar.show()
			self.__ShowButtons = False
		else:
			#self.__HBoxToolBoxContainer.hide()
			self.MenuBar.hide()
			self.__ShowButtons = True

	###########################################
	#           search stuff begins           #
	###########################################

	def onFindActivate(self, widget):
		"""
		Set the focus on the Search entry
		"""
		if not self.__MenuItemSmallView.active:
			self.HBoxSearch.show()
			self.EntrySearch.grab_focus()

	def __EntrySearchFocusHandler(self, entry, event):
		self.HBoxSearch.hide()

	def search(self, widget = None):
		"""
		Perform the actions to make a search
		"""
		self.__lastTypeTime = time.time()
		gobject.timeout_add(1000,self.__searchTimer)

	def __searchTimer(self):
		diff = time.time() - self.__lastTypeTime
		text = self.EntrySearch.get_text().lower()
		if diff > 0.5 and diff < 1 or not text:
			core.mainLibrary.model.TextToSearch = text
			core.mainLibrary.refilter() 
			self.jumpToPlaying()
			return False
		if diff > 1.5:
			return False
		return True

	def clearEntrySearch(self, widget):
		"""
		Entry search cleaning
		"""
		self.EntrySearch.set_text('')

	###################################################
	#                  Play stuff                     #
	###################################################

	def switchPlay(self, widget):
		"""
		This metod enable/disable the playing. Works for the
		menuitem and for the play button.
		"""
		#
		# is really needed two controls?
		#
		active = widget.get_active()

		if (not active):
			core.Player.pause()
			self.__StatePlaying = False
		else:
			self.play()
			self.__StatePlaying = True
			self.jumpToPlaying()

		# Sync the two controls
		self.menuItemPlay.set_active(active)
		self.PlayButton.set_active(active)

	def play(self, widget = None):
		"""
		Play!!, but only if the state is not already playing
		"""
		if not self.__StatePlaying:
			location = core.Player.getLocation()

			if location == None:
				self.goNext()
				return

			if os.path.isfile(location):
				# and only if location is not None, if it is the case then
				# go for one file to play
				if (location == None):
					self.goNext()
			else:
				self.setLocation(location)
			core.Player.playIt()
			
	def simplePlay(self):
		'''
		
		'''
		self.PlayButton.set_active(False)
		self.PlayButton.set_active(True)

	def pause(self, widget = None):
		"""
		Pause method
		"""
		self.PlayButton.set_active(False)

	def goPrev(self, widget = None):
		"""
		Go to play the previous song. If no previous song was played in the
		current session, then plays the previous song in the library
		"""
		import gst
		if core.Player.getLocation():
			nanos = core.Player.query_position(gst.FORMAT_TIME)[0]
			ts = (nanos / gst.SECOND)
			cmins, cseconds = map(int, divmod(ts, 60))
			if cseconds > 5:
				self.__LastPlayed.pop()
				self.setLocation(core.Player.getLocation())
				return 
		if len(self.__LastPlayed) > 1:
			#remove the last played since it's the same that we are playing.
			self.__LastPlayed.pop()
			self.setLocation(self.__LastPlayed.pop())
			self.PlayButton.set_active(False)
			self.PlayButton.set_active(True)
		else:
			iter = core.mainLibrary.model.basemodel.search_iter_on_column(
						self.christineConf.getString('backend/last_played'), 
						PATH)
			if iter == None:
				return False
			if not core.mainLibrary.tv.get_model().iter_is_valid(iter):
				return False
			path = core.mainLibrary.tv.get_model().get_path(iter)
			if path == None:
				return False
			if (path > 0):
				path = (path[0] -1,)
			elif (path[0] > -1):
				iter     = core.mainLibrary.tv.get_model().get_iter(path)
				location = core.mainLibrary.model.getValue(iter, PATH)
				self.setLocation(location)

				# This avoid the return to the last played song
				# wich is the next in the list.
				self.__LastPlayed.pop()
				self.PlayButton.set_active(False)
				self.PlayButton.set_active(True)

	def goNext(self, widget = None):
		"""
		Find a new file to play. in some cases relay on self.getNextInList
		"""
		# resetting the self.__LocationCount to 0 as we have a new file :-)
		self.__LocationCount = 0
		# Look for a file in the queue. Iter should not be None in the case
		# there where something in the queue
		model = core.Queue.tv.get_model()
		iter  = model.get_iter_first()

		if isinstance(iter,gtk.TreeIter):
			location = core.Queue.model.get_value(iter,PATH)
			self.setLocation(location)
			self.jumpToPlaying()
			core.Queue.remove(iter)
			self.PlayButton.set_active(False)
			self.PlayButton.set_active(True)
		else:
			#self.interface.Queue.scroll.hide()
			if (self.__MenuItemShuffle.get_active()):
				Elements = len (core.mainLibrary.tv.get_model()) - 1
				if Elements < 0:
					return
				randompath = 0
				if int(Elements) > 1:
					randompath = randint(0,int(Elements)-1)
				filename = core.mainLibrary.tv.get_model()[randompath][PATH]
				if (not filename in self.__LastPlayed) or \
						(self.christineConf.getBool('control/repeat')) and filename:
						self.setLocation(filename)
						self.simplePlay()
				else:
					self.getNextInList()
					self.simplePlay()
			else:
				self.getNextInList()

	def getNextInList(self):
		"""
		Gets the next item in list
		"""
		path = self.christineConf.getString('backend/last_played')

		if (path == None):
			filename = self.christineConf.getString('backend/last_played')
			iter = core.mainLibrary.model.basemodel.search_iter_on_column(filename, PATH)
			if (iter == None):
				iter     = core.mainLibrary.tv.get_model().get_iter_first()
				filename = core.mainLibrary.model.getValue(iter, PATH)
			self.setLocation(filename)
		else:
			iter = core.mainLibrary.model.search(path, PATH)
			if (iter != None):
				iter = core.mainLibrary.iter_next(iter)
			else:
				iter = core.mainLibrary.tv.get_model().get_iter_first()
			try:
				self.setLocation(core.mainLibrary.model.getValue(iter, PATH))
				self.simplePlay()
			except:
				self.setScale('', '', b = 0)
				self.setLocation(path)
				self.PlayButton.set_active(False)

	def onScaleChanged(self, scale, a, value = None):
		"""
		Callback on the value changed signal on position scale
		"""
		value = (int(core.Display.value * self.__TimeTotal) / gst.SECOND)
		self.__ScaleMoving = False
		if (value < 0):
			value = 0
		core.Player.seekTo(value)

	def setScale(self, scale, a, b):
		"""
		This method changes the scale value
		"""
		self.__ScaleMoving = True
		self.__ScaleValue  = b
		self.__ScaleMoving = False

	def jumpToPlaying(self, widget = None, location = None):
		"""
		This method jumps and select the file
		specified in the path.
		If path is not specified then try to
		select the playing one
		"""
		if not location or not isinstance(location, str):
			location = core.Player.getLocation()
		iter = core.mainLibrary.model.basemodel.search_iter_on_column(location, PATH)
		if iter:
			if self.__StatePlaying:
				pix  = self.share.getImageFromPix('christine-sound')
				pix  = pix.scale_simple(20, 20,	gtk.gdk.INTERP_BILINEAR)
				core.mainLibrary.set(iter, PIX, pix)
			iter = core.mainLibrary.model.get_sorted_iter(iter)
			npath = core.mainLibrary.model.sorted_path(iter)
			if npath and npath[0]:
				core.mainLibrary.tv.scroll_to_cell(npath, None, True, 0.5, 0.5)
				core.mainLibrary.tv.set_cursor(npath)

	def jumpTo(self, widget):
		"""
		Creates a gtk.Dialog box where
		the user specify the minute and second
		where to the song/video should be.
		"""
		# if self.__TimeTotal is not defined then
		# there is no media in player, so
		# there is no way to "jump to" any place.
		if not self.__TimeTotal:
			return False

		XML    = self.share.getTemplate('JumpTo')
		dialog = XML['dialog']
		mins = divmod((self.__TimeTotal / gst.SECOND), 60)[0]
		#Current minute and current second
		nanos      = core.Player.query_position(gst.FORMAT_TIME)[0]
		ts         = (nanos / gst.SECOND)
		(cmins, cseconds) = map(int, divmod(ts, 60))
		mins_adj = gtk.Adjustment(value = 0, lower = 0, upper = mins, step_incr = 1)
		secs_adj = gtk.Adjustment(value = 0, lower = 0, upper = 59, step_incr = 1)
		ok_button = XML['okbutton']
		mins_scale = XML['mins']
		secs_scale = XML['secs']
		mins_scale.connect('key-press-event', self.jumpToOkClicked, ok_button)
		secs_scale.connect('key-press-event', self.jumpToOkClicked, ok_button)
		mins_scale.set_adjustment(mins_adj)
		mins_scale.set_value(cmins)
		secs_scale.set_adjustment(secs_adj)
		secs_scale.set_value(cseconds)
		response = dialog.run()
		dialog.destroy()
		if response == gtk.RESPONSE_OK:
			time = (mins_scale.get_value() * 60) + secs_scale.get_value()
			if time > self.__TimeTotal:
				time = self.__TimeTotal
			core.Player.seekTo(time)

	def jumpToOkClicked(self, widget, event, button):
		"""
		Jumpo to Accept button
		"""
		if event.keyval in (gtk.gdk.keyval_from_name('Return'),
					gtk.gdk.keyval_from_name('KP_Enter')):
			button.emit('clicked')

	def decreaseVolume(self, widget = None):
		"""
		Decrease the volume
		"""
		volume = (self.__HScaleVolume.get_value() - 0.1)
		if (volume < 0):
			volume = 0
		self.__HScaleVolume.set_value(volume)

	def increaseVolume(self, widget = None):
		"""
		Increase the volume
		"""
		volume = (self.__HScaleVolume.get_value() + 0.1)
		self.__HScaleVolume.set_value(volume)

	def mute(self, widget):
		"""
		Set mute
		"""
		if (widget.get_active()):
			self.__Volume = self.__HScaleVolume.get_value()
			self.__HScaleVolume.set_value(0.0)
		else:
			self.__HScaleVolume.set_value(self.__Volume)

	####################################################
	#               library stuff begins               #
	####################################################

	def importFile(self, widget, queue = False):
		"""
		Import a file or files
		first argument is a widget, second argument
		is an optional  boolean value that defines
		if the files are going to queue or not
		"""
		XML = self.share.getTemplate('FileSelector')
		fs  = XML['fs']
		uri = self.christineConf.getString("ui/LastFolder")
		if uri:
			fs.set_uri('file://'+uri)
		response = fs.run()
		files    = fs.get_filenames()
		fs.destroy()
		if response == gtk.RESPONSE_OK:
			if queue:
				core.Queue.addFiles(files)
			else:
				core.mainLibrary.addFiles(files)
			path = os.path.join(os.path.split(files[0])[:-1])[0]
			self.christineConf.setValue("ui/LastFolder",path)
	
	def importFolder(self, widget):
		XML  = self.share.getTemplate('directorySelector')
		ds   = XML['ds']
		walk = XML['walk']
		uri = self.christineConf.getString("ui/LastFolder")
		if uri:
			ds.set_uri('file://'+uri)
		ds.show_all()
		ds.connect('response', self.__do_import_folder_response, walk)
	
	def __do_import_folder_response(self, ds, response, walk):
		if response == gtk.RESPONSE_OK:
			filenames = ds.get_filenames()
			print walk
			walkdir = walk.get_active()
			self.christineConf.setValue("ui/LastFolder",filenames[0])
			ds.destroy()
			core.mainLibrary.importFolder(filenames, walkdir)
			return True
		ds.destroy()
	

	def importToQueue(self, widget):
		"""
		Import file to queue
		"""
		self.importFile('', True)

	########################################
	#          PLayer section              #
	########################################

	def do_gst_error(self, player, emsg):
		if emsg.find('File not found'):
			self.__Logger.warning(emsg)
			self.goNext()
			return
		error(emsg)
	
	def do_end_of_stream(self, player):
		self.goNext()

	def do_message_tag(self, player):
		self.setTags()
	
	def do_buffering(self, player, percent):
		core.Display.setText("%d" % percent)
		core.Display.setScale((percent / 100))
		if percent in(0, 100):
			core.Display.setText("")

	def checkTimeOnMedia(self):
		"""
		Update the time showed in the player
		"""
		try:
			self.__streamLength()
			nanos = core.Player.query_position(gst.FORMAT_TIME)[0]
			ts = (nanos / gst.SECOND)
			time = "%02d:%02d" % divmod(ts, 60)
			time_total = "%02d:%02d" % divmod((self.__TimeTotal / gst.SECOND), 60)
			#set ts=0 if ts if less than 0
			ts = [ts, long(0)][ts < 0]
			if nanos > 0 and self.__TimeTotal > 0:
				currenttime = nanos / float(self.__TimeTotal)
				core.Display.setText("%s/%s"%(time, time_total))
				if currenttime >= 0 and currenttime <= 1:
					core.Display.setScale(currenttime)
		except:
			pass
		return True

	def __streamLength(self):
		"""
		Catches the lenght of the media and update it in the
		player
		"""
		location = core.Player.getLocation()
		if not location:
			return True
		if (location.split(':')[0] == 'http'):
			self.__TimeTotal = 0
			return True
		try:
			self.__TimeTotal = core.Player.query_duration(gst.FORMAT_TIME)[0]
			ts               = (self.__TimeTotal / gst.SECOND)
			text             = "%02d:%02d" % divmod(ts, 60)
			self.__ErrorStreamCount = 0
			iter = core.mainLibrary.model.basemodel.search_iter_on_column(location, PATH)
			if iter is not None:
				time= core.mainLibrary.model.get_value(iter, TIME)
				if time != text:
					core.mainLibrary.updateData(core.Player.getLocation(),
								time=text)
			self.__LocationCount = 0
			return False
		except gst.QueryError, e:
			self.__ErrorStreamCount += 1
			if (self.__ErrorStreamCount > 10):
				self.setLocation(core.Player.getLocation())
				self.simplePlay()

			return True

	def setTags(self, widget = "", b = ""):
		"""
		This method fetchs the data from the song/media in the player.
		Then, ask to the library to update the values on it.
		"""
		title     = core.Player.getTag('title').replace('_', ' ')
		artist    = core.Player.getTag('artist')
		album     = core.Player.getTag('album')
		genre     = core.Player.getTag('genre')
		tags = [title,artist,album,genre]
		if tags == self.__LastTags:
			return True
		else:
			self.__LastTags = tags
		if isinstance(genre, list):
			genre = ','.join(genre)
		elif isinstance(genre, basestring):
			genre = ""
		track_number = core.Player.getTag('track-number')
		if isinstance(track_number,basestring):
			if track_number.isdigit():
				track_number = int(track_number)
			else:
				track_number = 0
		if not title:
			title = os.path.split(core.Player.getLocation())[1]
			title = '.'.join(title.split('.')[:-1])
		title    = self.strip_XML_entities(title)
		# Sets window title, which it will be our current song :-)
		self.coreWindow.set_title("%s - Christine" % title)
		tags = {'title': title, 'artist': artist, 'album': album,
			'track_number': track_number, 'genre': genre}
		self.Events.emit('gotTags', tags)
		self.visualModePlayer()

	########################################
	#             Gtk modes                #
	########################################

	def visualModePlayer(self, widget = None):
		"""
		Simple or complete visualization
		"""
		isPlaying = False
		state = core.Player.getState()[1]
		if gst.State(gst.STATE_PLAYING) is state:
			isPlaying = True
		comp = core.Player.isVideo() or \
				self.christineConf.getBool('ui/visualization')
		core.Player.set_property('visible', comp)

	def cleanLibrary(self,widget):
		xml = self.share.getTemplate("deleteQuestion")
		dialog = xml["dialog"]
		response = dialog.run()
		if response == -5:
			core.mainLibrary.clear()
		dialog.destroy()

	def openRemote(self,widget):
		import libchristine.gui.openRemote 
		libchristine.gui.openRemote.openRemote()

	def showGtkAbout(self, widget):
		"""
		Show the about dialog
		"""
		import libchristine.gui.About
		a = libchristine.gui.About.guiAbout()
		a.about.set_transient_for(self.coreWindow)
		a.run()

	def showGtkPreferences(self, widget):
		"""
		Show the preferences dialog
		"""
		import libchristine.gui.Preferences
		libchristine.gui.Preferences.guiPreferences()

	def ShowHideSidePanel(self, widget):
		'''
		Show or hide the side Panel 
		@param widget:
		'''
		self.VBoxList.set_property('visible', widget.get_active())
		self.christineConf.setValue('ui/sidepanel', widget.get_active())

	def quitGtk(self, widget = None):
		core.Player.stop()
		close()
	
	def runGtk(self):
		"""
		GTK application running
		"""
		gtk.main()

def add_items_to_queue(obj, c):
	if c == None or c.coreWindow.get_property('window'):
		for i in sys.argv[1:]:
			if os.path.exists(i) and os.path.isfile(i):
				obj.add_to_queue(i)
		return False
	return True


def runChristine():
	'''
	This function handles parameters for christine.
	'''
	if os.name == 'nt':
		ex = Exception
	else:
		import dbus
		ex = dbus.exceptions.DBusException
	try:
		import dbus
		from dbus.mainloop.glib import DBusGMainLoop
		main_loop = DBusGMainLoop()
		DBUS_SESSION = dbus.SessionBus(mainloop = main_loop)
		obj = DBUS_SESSION.get_object('org.christine', '/org/christine',)
		c = None
		add_items_to_queue(obj,c)
		sys.exit()
	except ex, e:
		print e
		try:
			import libchristine.christine_dbus.christineDBus
			a = christineDBus()
		except:
			pass
		c = Christine()
		for i in sys.argv[1:]:
			if os.path.exists(i) and os.path.isfile(i):
				c.Queue.add(i)
		f = open(PIDFILE,'w')
		f.write('%d'%(os.getpid()))
		f.close()
	except Exception, e:
		print e
		#BugReport()
	gtk.main()
	

