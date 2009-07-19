#! /usr/bin/env python
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
# @category  Multimedia
# @package   Christine
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import pango

#import os
import sys
import random
import time
import gtk
import gtk.gdk
import pygst; pygst.require('0.10')
import gst.interfaces
import gobject
import os
import signal
from  libchristine.Plugins import Manager
from libchristine.Translator import translate
from libchristine.gui.GtkMisc import GtkMisc, error
from libchristine.gui.Preferences import guiPreferences
from libchristine.gui.About import guiAbout
from libchristine.gui.Display import Display
from libchristine.globalvars import  BUGURL
from libchristine.ui import interface
from libchristine.gui.openRemote import openRemote
from libchristine.Library import library, queue,PATH, HAVE_TAGS
from libchristine.Library import PIX,TIME
from libchristine.Player import Player
from libchristine.Share import Share
#from libchristine.christineConf import christineConf
from libchristine.sources_list import sources_list, LIST_NAME, LIST_TYPE, LIST_EXTRA
from libchristine.Logger import LoggerManager
#from libchristine.Events import christineEvents
from libchristine.christine_dbus import *
from libchristine.options import options
import webbrowser
import gc

opts = options()

#gc.enable()


def close(*args):
	pidfile = 	os.path.join(os.environ['HOME'],'.christine','christine.pid')
	if os.path.exists(pidfile):
		os.unlink(pidfile)
	sys.exit()
	gtk.main_quit()


signal.signal(signal.SIGTERM, close)

if (gtk.gtk_version < (2, 10, 0)):
	print translate('Gtk+ 2.10 or better is required')
	sys.exit()

class Christine(GtkMisc):
	def __init__(self):
		"""
		Constructor, this method will init the gtk_misc parent class,
		initialize the gnome ui client, create the XML interface descriptor,
		initialize class variables and create some timeouts calls
		"""
		self.__Logger = LoggerManager().getLogger('Christine')
		GtkMisc.__init__(self)

		self.share   = Share()
		self.christineConf   = christineConf()
		self.interface = interface()
		self.interface.coreClass = self
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
		#tryIcon()

		self.christineConf.notifyAdd('ui/show_in_notification_area',
				lambda cl,cnx,entry,widget: \
				self.interface.TrayIcon.TrayIcon.set_visible(entry.get_value().get_bool()))

		gobject.timeout_add(1000, self.checkTimeOnMedia)
		# Creating the player and build the GUI interface
		self.__Player = Player()
		self.__buildInterface()
		self.coreWindow.show()
		self.HBoxSearch.hide()
		plugins_manager = Manager()
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
		self.mainSpace.append_page(self.__Player,None)
		self.__Player.bus.add_watch(self.__handlerMessage)

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
		self.coreWindow.set_icon(self.share.getImageFromPix('logo'))
		# Uncoment next lines if you want to use RGBA in your theme
		width = self.christineConf.getInt('ui/width')
		height = self.christineConf.getInt('ui/height')
		if not width or not  height:
			width, height = (800,600)
		self.coreWindow.set_default_size(width, height)
		self.coreWindow.connect("destroy",lambda widget: widget.hide())
		self.coreWindow.connect("scroll-event",self.changeVolumeWithScroll)
		self.coreWindow.connect("key-press-event",self.onWindowkeyPressEvent)
		self.coreWindow.connect('size-allocate', self.__on_corewindow_resized)
		self.interface.coreWindow = self.coreWindow

		self.PlayButton   = xml['ToggleButtonPlay']
		self.interface.playButton =  self.PlayButton
		self.menuItemPlay = xml['MenuItemPlay']

		openremotemitem = xml['open_remote1']
		openremotemitem.connect('activate', lambda widget: openRemote())
		self.Menus = {}
		for i in ('media', 'edit', 'control', 'help'):
			self.Menus["%s" % i] = xml["%s_menu" % i].get_submenu()

		self.__HBoxCairoDisplay = xml['HBoxCairoDisplay']

		# Create the display and attach it to the main window
		self.__Display = Display()
		self.__Display.connect('value-changed', self.onScaleChanged)
		self.__HBoxCairoDisplay.pack_start(self.__Display, True, True, 0)
		self.__Display.show()

		# Create the library by calling to libs_christine.library class
		self.mainLibrary  = library()
		lastSourceUsed = self.christineConf.get('backend/last_source')
		if not lastSourceUsed:
			lastSourceUsed = 'music'
		self.mainLibrary.loadLibrary(lastSourceUsed)
		self.mainLibrary.tv.show()

		self.mainLibrary.scroll
		#self.libraryVBox = xml['libraryVBox']
		self.mainSpace.append_page(self.mainLibrary.scroll, None)
		self.mainSpace.set_current_page(1)
		self.mainSpace.show_all()
		
		self.sideNotebook = xml['sideNotebook']

		self.Queue = queue()
		label = gtk.Label(_('Queue'))
		label.set_angle(90)
		self.sideNotebook.append_page(self.Queue.scroll, label)
		#self.VBoxList.pack_start(self.Queue.scroll, False, False, 0)
		self.queue_mi = xml['Queue']
		self.queue_mi.connect('activate', lambda x: self.sideNotebook.set_current_page(0))
		self.Queue.tv.connect('row-activated',   self.Queue.itemActivated)

		self.sourcesList = sources_list()
		label = gtk.Label(_('Sources List'))
		label.set_angle(90)
		self.sources_mi = xml['SourcesList']
		self.sources_mi.connect('activate', lambda x: self.sideNotebook.set_current_page(1))
		self.sideNotebook.append_page(self.sourcesList.vbox, label)
		#self.VBoxList.pack_start(self.sourcesList.vbox)
		self.sourcesList.treeview.connect('row-activated',
				self.__srcListRowActivated)
		self.sourcesList.vbox.show_all()
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
		
		#self.__BothSr = xml['both_sr']
		#self.__NoneSr = xml['none_sr']

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
		URL = 'https://translations.launchpad.net/christine/0.1/'
		translateMenuItem.connect('activate', lambda widget: webbrowser.open(URL))

		reportaBug = xml['reportABug']
		reportaBug.connect('activate', lambda widget: webbrowser.open(BUGURL))

		self.__HBoxToolBoxContainer = xml['HBoxToolBoxContainer']
		self.__HBoxToolBoxContainer.set_property('events',gtk.gdk.ENTER_NOTIFY|gtk.gdk.SCROLL_MASK)
		self.__HBoxToolBoxContainer.connect("scroll-event",self.changeVolumeWithScroll)

		self.__HBoxButtonBox		= xml['HBoxButtonBox']
		self.__HBoxButtonBox.set_property('events',gtk.gdk.ENTER_NOTIFY|gtk.gdk.SCROLL_MASK)
		self.__HBoxButtonBox.connect('scroll-event',self.changeVolumeWithScroll)

		self.__HScaleVolume         = xml['HScaleVolume']
		self.__HScaleVolume.connect("scroll-event",self.changeVolumeWithScroll)

		volume = self.christineConf.getFloat('control/volume')
		if (volume):
			self.__HScaleVolume.set_value(volume)
		else:
			self.__HScaleVolume.set_value(0.8)

		self.__HBoxToolBoxContainerMini = self.__HBoxToolBoxContainer
		self.jumpToPlaying(location = self.christineConf.getString('backend/last_played'))
		self.__pidginMessage = self.christineConf.getString('pidgin/message')
		gobject.timeout_add(500, self.__check_items_on_media)
		#gobject.idle_add(self.__check_items_on_media)
	
	def __check_items_on_media(self):
		size = len(self.mainLibrary.model.basemodel)
		randompath = ((int(size * random.random())),)
		if randompath[0]:
			filepath, tags = self.mainLibrary.model.basemodel.get(
							self.mainLibrary.model.basemodel.get_iter(randompath),
							PATH,HAVE_TAGS)
			if not tags:
				self.mainLibrary.check_single_file_data(filepath)
		return True

	def __srcListRowActivated(self, treeview, path, column):
		model = treeview.get_model()
		fname, ftype, fextra = model.get(model.get_iter(path), LIST_NAME, LIST_TYPE, LIST_EXTRA)
		if ftype == 'source':
			if fname == 'Sources':
				return True
			self.mainLibrary.loadLibrary(fname)
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
				import urllib
				gate = urllib.FancyURLopener()
				urldesc = gate.open(location)

			if extension == "pls":
				for i in urldesc.readlines():
					print i
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

		self.__Player.stop()
		self.__Player.setLocation(filename)
		name = os.path.split(filename)[-1]
		self.__Display.setSong(name)
		self.__LastPlayed.append(filename)
		# enable the stream-length for the current song.
		# this will be stopped when we get the length
		gobject.timeout_add(100, self.__streamLength)
		# if we can't get the length, in more than 20
		# times in the same song, then, jump to the
		# next song
		if (self.__LocationCount > 20):
			self.goNext()
		else:
			self.__LocationCount +=1
		self.mainLibrary.tv.grab_focus()

	def stop(self, widget=None):
		"""
		Stop the player
		"""
		self.__Player.stop()

	def changeVolume(self, widget):
		"""
		Callback for the volume scale widget
		"""
		value = widget.get_value()
		self.__Player.setVolume(value)
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
		self.__Player.setVisualization(widget.get_active())
		page = [1,0][widget.get_active()]
		self.mainSpace.set_current_page(page)

	def toggleFullScreen(self, widget = None):
		"""
		Set the full Screen mode
		"""
		# Only if we are not in FullScreen and we are playing a video.
		# FIXME: We must enable the full screen if christine has
		#        visualization enabled
		if (not self.__IsFullScreen):
			if ((self.__Player.isVideo()) or (self.christineConf.getBool('ui/visualization'))):
				self.coreWindow.fullscreen()
				#self.mainLibray.scroll.set_size_request(0,0)
				self.__VBoxList.set_size_request(0,0)

				self.__IsFullScreen = True
			else:
				self.__Logger.warning('Full screen with no visualization')
				self.coreWindow.fullscreen()
				self.__IsFullScreen = True
		else:
		# Non-full screen mode.
		# hide if we are not playing a video nor
		# visualization.
			if ((not self.__Player.isVideo()) and (not self.christineConf.getBool('ui/visualization'))):
				self.__Player.hide()
			self.mainLibrary.scroll.set_size_request(200,200)
			self.__VBoxList.set_size_request(150,0)

			self.coreWindow.unfullscreen()
			self.__IsFullScreen = False

	def onWindowkeyPressEvent(self, player, event):
		"""
		Handler for the key press events in the window
		"""
		if (event.keyval == gtk.gdk.keyval_from_name('g')):
			self.viewPlayButtons()
		elif (event.keyval == gtk.gdk.keyval_from_name('Page_Down')):
			if (self.__IsFullScreen):
				self.goNext()
		elif (event.keyval == gtk.gdk.keyval_from_name('Page_Up')):
			if (self.__IsFullScreen):
				self.goPrev()
				return True
		elif ( event.keyval == gtk.gdk.keyval_from_name('f')):
			if (self.__IsFullScreen):
				self.toggleFullScreen()

	def viewPlayButtons(self, widget = None):
		"""
		This show/hide the player buttons. Suppossed to work only on
		fullscreen mode
		"""
		if (not self.__IsFullScreen):
			return True

		if (self.__ShowButtons):
			self.__HBoxToolBoxContainerMini.show()
			self.MenuBar.show()
			self.__ShowButtons = False
		else:
			self.__HBoxToolBoxContainerMini.hide()
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
			self.mainLibrary.model.TextToSearch = text
			self.mainLibrary.refilter() 
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
			self.__Player.pause()
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
			location = self.__Player.getLocation()

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
			self.__Player.playIt()
			
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
		if (len(self.__LastPlayed) > 1):
			#remove the last played since it's the same that we are playing.
			self.__LastPlayed.pop()
			self.setLocation(self.__LastPlayed.pop())
			self.PlayButton.set_active(False)
			self.PlayButton.set_active(True)
		else:
			iter = self.mainLibrary.model.basemodel.search_iter_on_column(
						self.christineConf.getString('backend/last_played'), 
						PATH)
			if iter == None:
				return False
			if not self.mainLibrary.tv.get_model().iter_is_valid(iter):
				return False
			path = self.mainLibrary.tv.get_model().get_path(iter)
			if path == None:
				return False
			if (path > 0):
				path = (path[0] -1,)
			elif (path[0] > -1):
				iter     = self.mainLibrary.tv.get_model().get_iter(path)
				location = self.mainLibrary.model.getValue(iter, PATH)
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
		model = self.Queue.tv.get_model()
		iter  = model.get_iter_first()

		if isinstance(iter,gtk.TreeIter):
			location = self.Queue.model.get_value(iter,PATH)
			self.setLocation(location)
			self.jumpToPlaying()
			self.Queue.remove(iter)
			self.Queue.save()
			self.PlayButton.set_active(False)
			self.PlayButton.set_active(True)
		else:
			#self.interface.Queue.scroll.hide()
			if (self.__MenuItemShuffle.get_active()):
				Elements = len (self.mainLibrary.tv.get_model()) - 1
				if Elements < 0:
					return True
				randompath = ((int(Elements * random.random())),)
				filename = self.mainLibrary.tv.get_model()[randompath][PATH]
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
			iter = self.mainLibrary.model.basemodel.search_iter_on_column(filename, PATH)
			if (iter == None):
				iter     = self.mainLibrary.tv.get_model().get_iter_first()
				filename = self.mainLibrary.model.getValue(iter, PATH)
			self.setLocation(filename)
		else:
			iter = self.mainLibrary.model.search(path, PATH)
			if (iter != None):
				iter = self.mainLibrary.iter_next(iter)
			else:
				iter = self.mainLibrary.tv.get_model().get_iter_first()
			try:
				self.setLocation(self.mainLibrary.model.getValue(iter, PATH))
				self.simplePlay()
			except:
				self.setScale('', '', b = 0)
				self.setLocation(path)
				self.PlayButton.set_active(False)

	def onScaleChanged(self, scale, a, value = None):
		"""
		Callback on the value changed signal on position scale
		"""
		value = (int(self.__Display.value * self.__TimeTotal) / gst.SECOND)
		self.__ScaleMoving = False
		if (value < 0):
			value = 0
		self.__Player.seekTo(value)

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
			location = self.__Player.getLocation()
		iter = self.mainLibrary.model.basemodel.search_iter_on_column(location, PATH)
		if iter:
			if self.__StatePlaying:
				pix  = self.share.getImageFromPix('sound')
				pix  = pix.scale_simple(20, 20,	gtk.gdk.INTERP_BILINEAR)
				self.mainLibrary.set(iter, PIX, pix)
			iter = self.mainLibrary.model.get_sorted_iter(iter)
			npath = self.mainLibrary.model.sorted_path(iter)
			if npath and npath[0]:
				self.mainLibrary.tv.scroll_to_cell(npath, None, True, 0.5, 0.5)
				self.mainLibrary.tv.set_cursor(npath)

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
		dialog.set_icon(self.share.getImageFromPix('logo'))
		mins = divmod((self.__TimeTotal / gst.SECOND), 60)[0]
		#Current minute and current second
		nanos      = self.__Player.query_position(gst.FORMAT_TIME)[0]
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
			self.__Player.seekTo(time)

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
		fs.set_icon(self.share.getImageFromPix('logo'))
		response = fs.run()
		files    = fs.get_filenames()
		fs.destroy()
		if response == gtk.RESPONSE_OK:
			self.addFiles(files = files, queue = queue)
			path = os.path.join(os.path.split(files[0])[:-1])[0]
			self.christineConf.setValue("ui/LastFolder",path)

	def importFolder(self, widget):
		"""
		This is the 'simple' way to import folders
		Creates and run a filechooser dialog to
		select the dir.
		A Checkbox let you set if the import will be
		recursive.
		"""
		XML  = self.share.getTemplate('directorySelector')
		ds   = XML['ds']
		walk = XML['walk']
		uri = self.christineConf.getString("ui/LastFolder")
		if uri:
			ds.set_uri('file://'+uri)
		ds.set_icon(self.share.getImageFromPix('logo'))
		response  = ds.run()
		filenames = ds.get_filenames()
		if response == gtk.RESPONSE_OK:
			self.christineConf.setValue("ui/LastFolder",filenames[0])
			ds.destroy()
			for i in filenames:
				if walk.get_active():
					self.addDirectories(i)
				else:
					files = [os.path.join(i, k) \
						for k in os.listdir(i) \
						if os.path.isfile(os.path.join(i, k))]
					if files:
						self.addFiles(files = files)
			return True
		ds.destroy()

	def addDirectory(self, dir):
		"""
		This add a single directory, is simplier that addDirectories
		because there is no need to dig
		"""
		files = os.listdir(dir)
		f     = []
		self.f = []
		extensions = self.christineConf.getString('backend/allowed_files').split(',')
		for i in files:
			ext = i.split('.').pop()
			if ext in extensions:
				f.append(i)
		files = f
		self.addFiles(files)

	def addDirectories(self, dir):
		"""
		Recursive import, first and only argument
		is the dir where to digg
		"""
		# dig looking for files
		a         = os.walk(dir)
		f         = []
		filenames = []
		self.f = []
		xml = self.share.getTemplate('walkdirectories')
		dialog = xml['dialog1']
		progress = xml['progressbar1']
		label = xml['label1']
		self.__walking = True
		gobject.idle_add(self.__walkDirectories, a, f, filenames, label, dialog)
		self.__walkProgressPulse(progress)
		dialog.set_modal(False)
		response = dialog.run()
		if response:
			self.__walking = False
		dialog.destroy()

	def __walkProgressPulse(self, progress):
		progress.pulse()
		while gtk.events_pending():
			gtk.main_iteration_do()
		return not self.__walking

	def __walkDirectories(self, a, f, filenames, label, dialog):
		if not self.__walking:
			return False
		try:
			(dirpath, dirnames, files) = a.next()
			del dirnames
			filenames.append([dirpath, files])
			npath = self.encode_text(dirpath)
			label.set_text(translate('Exploring') + '%s'%npath)
			allowdexts = self.christineConf.getString('backend/allowed_files')
			allowdexts = allowdexts.split(',')
			for path in filenames[-1][1]:
				ext    = path.split('.').pop().lower()
				exists = os.path.join(filenames[-1][0], path) in self.f
				if ext in allowdexts and not exists:
					f.append(os.path.join(filenames[-1][0],path))
		except StopIteration:
			dialog.destroy()
			if f:
				self.addFiles(files = f)
			return False
		return True

	def __addFile(self, list = None, data = None,queue = False):
		"""
		Add a single file, to the library or queue.
		the files are taken from the self.__FilesToAdd
		list. the only one argument is queue, wich defines
		if the importing is to the queue
		"""
		if not isinstance(queue, bool):
			queue = False
		library = (self.mainLibrary, self.Queue)[queue]
		gobject.idle_add(self.__addFileCycle, library)

	def __addFileCycle(self, library):
		for i in  xrange(1,2):
			if self.__FilesToAdd:
				new_file = self.__FilesToAdd.pop()
				library.add(new_file)
				self.__updateAddProgressBar(new_file)
			else:
				library.save()
				self.__AddWindow.destroy()
				self.__walking = False
				return False
		return True

	def __updateAddProgressBar(self, file):
		length = len(self.__FilesToAdd)
		self.__Percentage = 1
		if length:
			self.__Percentage = (1 - (length / float(self.__TimeTotalNFiles)))
		if self.__Percentage > 1.0:
			self.__Percentage = 1.0
		# Setting the value and text in the progressbar
		self.__AddProgress.set_fraction(self.__Percentage)
		rest = (self.__TimeTotalNFiles - length)
		text = "%d/%d" % (rest, self.__TimeTotalNFiles)
		self.__AddProgress.set_text(text)
		filename = self.encode_text(os.path.split(file)[1])
		self.__AddFileLabel.set_text(filename)
		return length

	def addFiles(self, widget = None, files = None, queue = False):
		"""
		Add files to the library or to the queue
		"""
		XML = self.share.getTemplate('addFiles')
		XML.signal_autoconnect(self)

		self.__AddWindow       = XML['window']
		self.__AddWindow.set_transient_for(self.coreWindow)
		self.__AddProgress     = XML['progressbar']
		self.__AddCloseButton  = XML['close']
		self.__AddCloseButton.connect('clicked',lambda *args: self.importCancel())
		self.__AddFileLabel    = XML['file_label']
		self.__AddFileLabel.set_text('None')
		self.__AddWindow.connect('destroy', lambda *args: self.importCancel())
		self.__AddWindow.show_all()

		self.__AddCloseButton.grab_add()
		# Be sure that we are working with a list of files
		if not isinstance(files, list):
			raise TypeError, "files must be List, got %s" % type(files)
		files.reverse()
		# Global variable to save temporal files and paths
		self.__FilesToAdd = []
		self.__Paths      = []
		self.mainLibrary.model.basemodel.foreach(self.getPaths)
		extensions = self.christineConf.getString('backend/allowed_files')
		extensions = extensions.split(',')
		iterator = iter(files)
		while True:
			try:
				i = iterator.next()
				ext = i.split('.').pop().lower()
				if (not i in self.__Paths) and \
						(ext in extensions):
					self.__FilesToAdd.append(i)
			except StopIteration:
				break
		self.__Percentage      = 0
		self.__TimeTotalNFiles = len(self.__FilesToAdd)
		self.__addFile(queue=queue)

	def getPaths(self, model, path, iter):
		"""
		Gets path from
		"""
		self.__Paths.append(model.get_value(iter, PATH))

	def importCancel(self):
		"""
		Cancel de import stuff
		"""
		self.__AddCloseButton.grab_remove()
		self.__FilesToAdd = []
		self.__AddWindow.destroy()

	def importToQueue(self, widget):
		"""
		Import file to queue
		"""
		self.importFile('', True)

	########################################
	#          PLayer section              #
	########################################

	def __handlerMessage(self, a, b, c = None, d = None):
		"""
		Handle the messages from self.__Player
		"""
		type_file = b.type
		if (type_file == gst.MESSAGE_ERROR):
			if not os.path.isfile(self.__Player.getLocation()):
				if os.path.split(self.__Player.getLocation())[0] == '/':
					error(translate('File was not found, going to next file'))
					self.goNext()
			else:
				error(b.parse_error()[1])
		if (type_file == gst.MESSAGE_EOS):
			self.goNext()
		elif (type_file == gst.MESSAGE_TAG):
			self.__Player.foundTagCallback(b.parse_tag())
			self.setTags()
		elif (type_file == gst.MESSAGE_BUFFERING):
			percent = 0
			percent = b.structure['buffer-percent']
			self.__Display.setText("%d" % percent)
			self.__Display.setScale((percent / 100))
			if percent in(0, 100):
				self.__Display.setText("")
			return True
		return True

	def checkTimeOnMedia(self):
		"""
		Update the time showed in the player
		"""
		try:
			self.__streamLength()
			nanos      = self.__Player.query_position(gst.FORMAT_TIME)[0]
			ts         = (nanos / gst.SECOND)
			time       = "%02d:%02d" % divmod(ts, 60)
			time_total = "%02d:%02d" % divmod((self.__TimeTotal / gst.SECOND), 60)
			if (ts < 0):
				ts = long(0)
			if ((nanos > 0) and (self.__TimeTotal > 0)):
				currenttime = (nanos / float(self.__TimeTotal))
				self.__Display.setText("%s/%s" % (time, time_total))
				if ((currenttime >= 0) and (currenttime <= 1)):
					self.__Display.setScale(currenttime)
		except gst.QueryError:
			pass
		return True

	def __streamLength(self):
		"""
		Catches the lenght of the media and update it in the
		player
		"""
		location = self.__Player.getLocation()
		if not location:
			return True
		if (location.split(':')[0] == 'http'):
			self.__TimeTotal = 0
			return True
		try:
			self.__TimeTotal = self.__Player.query_duration(gst.FORMAT_TIME)[0]
			ts               = (self.__TimeTotal / gst.SECOND)
			text             = "%02d:%02d" % divmod(ts, 60)
			self.__ErrorStreamCount = 0
			iter = self.mainLibrary.model.basemodel.search_iter_on_column(location, PATH)
			if (iter is not None):
				time= self.mainLibrary.model.get_value(iter, TIME)
				if (time != text):
					self.mainLibrary.updateData(self.__Player.getLocation(),
								time=text)
			self.__LocationCount = 0
			return False
		except gst.QueryError, e:
			self.__ErrorStreamCount += 1
			if (self.__ErrorStreamCount > 10):
				self.setLocation(self.__Player.getLocation())
				self.simplePlay()

			return True

	def setTags(self, widget = "", b = ""):
		"""
		This method fetchs the data from the song/media in the player.
		Then, ask to the library to update the values on it.
		"""
		title     = self.__Player.getTag('title').replace('_', ' ')
		artist    = self.__Player.getTag('artist')
		album     = self.__Player.getTag('album')
		genre     = self.__Player.getTag('genre')
		tags = [title,artist,album,genre]
		if tags == self.__LastTags:
			return True
		else:
			self.__LastTags = tags
		if (type(genre) == type([])):
			genre = ','.join(genre)
		elif type(genre) != type(""):
			genre = ""
		track_number = self.__Player.getTag('track-number')
		if isinstance(track_number,str):
			if track_number.isdigit():
				track_number = int(track_number)
			else:
				track_number = 0
		if (title == ''):
			title = os.path.split(self.__Player.getLocation())[1]
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
		state = self.__Player.getState()[1]
		if gst.State(gst.STATE_PLAYING) is state:
			isPlaying = True
		if (self.__Player.isVideo()):
			self.mainSpace.set_current_page(1)
		else:
			page = [1,0][self.christineConf.getBool('ui/visualization') and isPlaying]
			self.mainSpace.set_current_page(page)

	def cleanLibrary(self,widget):
		xml = self.share.getTemplate("deleteQuestion")
		dialog = xml["dialog"]
		response = dialog.run()
		if response == -5:
			self.mainLibrary.clear()
		dialog.destroy()

	def showGtkAbout(self, widget):
		"""
		Show the about dialog
		"""
		a = guiAbout()
		a.about.set_transient_for(self.coreWindow)
		a.run()

	def showGtkPreferences(self, widget):
		"""
		Show the preferences dialog
		"""
		guiPreferences()

	def ShowHideSidePanel(self, widget):
		'''
		Show or hide the side Panel 
		@param widget:
		'''
		self.VBoxList.set_property('visible', widget.get_active())
		self.christineConf.setValue('ui/sidepanel', widget.get_active())

	def quitGtk(self, widget = None):
		self.__Player.stop()
		close()
	
	def runGtk(self):
		"""
		GTK application running
		"""
		gtk.main()

