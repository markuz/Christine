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
from libchristine.Translator import translate
from libchristine.gui.GtkMisc import GtkMisc, error
from libchristine.gui.Preferences import guiPreferences
from libchristine.gui.About import guiAbout
from libchristine.gui.Display import Display
from libchristine.globalvars import PROGRAMNAME, BUGURL
from libchristine.sqlitedb import sqlite3db
from libchristine.ui import interface
from libchristine.tryicon import tryIcon
from libchristine.gui.openRemote import openRemote
from libchristine.Library import library, queue,PATH, \
NAME,\
PIX,\
PLAY_COUNT,\
TIME
from libchristine.Player import Player
from libchristine.Share import Share
from libchristine.christineConf import christineConf
from libchristine.sources_list import sources_list, LIST_NAME
import logging
import webbrowser
import gc

gc.enable()


try:
	import pynotify
	pynotify.Urgency(pynotify.URGENCY_NORMAL)
	pynotify.init(PROGRAMNAME)
	version = pynotify.get_server_info()['version'].split('.')

	if (version < [0, 3, 6]):
		raise ImportError("server version is %d.%d.%d, 0.3.6 or major required" % version)

	PYNOTIFY = True
except ImportError:
	print 'no pynotify available'
	PYNOTIFY = False

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
		self.__Logger = logging.getLogger('Christine')
		GtkMisc.__init__(self)

		self.share   = Share()
		self.__christineGconf   = christineConf()
		self.__sqlite = sqlite3db()
		self.interface = interface()
		self.interface.coreClass = self

		# Class variables
		self.__ErrorStreamCount = 0
		self.__TimeTotal        = 0     # Nanosecs for audio/video file
		self.__LocationCount    = 0     # Count ns and jump if the file is not good
		self.__LastPlayed       = []
		self.__IterNatural      = None
		self.IterCurrentPlaying = None # Temporal store for the current iter playing
		self.__ScaleMoving      = False
		self.__StatePlaying     = False
		self.__IsFullScreen     = False
		self.__ShowButtons      = False
		self.__IsHidden         = False
		self.__LastTags			= []
		self.__lastTypeTime		= time.time()

		# Create the try icon.
		tryIcon()

		self.__christineGconf.notifyAdd('ui/show_in_notification_area',
				lambda cl,cnx,entry,widget: \
				self.interface.TrayIcon.TrayIcon.set_visible(entry.get_value().get_bool()))

		gobject.timeout_add(500, self.checkTimeOnMedia)
		# Creating the player and build the GUI interface
		self.__Player = Player()
		self.__buildInterface()
		self.coreWindow.show()
		self.HBoxSearch.hide()

	def __printEvent(self,widget,event):
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
		self.__VBoxCore.connect('scroll-event',self.__printEvent)
		self.__HBoxPlayer = xml['HBoxPlayer']
		self.__HBoxPlayer.connect('event',self.__printEvent)
		self.__HBoxPlayer.pack_start(self.__Player, True, True, 0)
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
		#Private widgets
		self.__HPanedListsBox = xml['HPanedListsBox']
		self.__VBoxTemporal   = xml['VBoxTemporal']
		#self.__ScrolledMusic  = xml["ScrolledMusic"]
		self.__VBoxList       = xml["VBoxList"]
		# Ends the call to widgets descriptors not connected by hadn

		# Gets window widget from glade template
		self.coreWindow = xml['WindowCore']
		self.coreWindow.connect("destroy",lambda widget: widget.hide())
		self.coreWindow.set_icon(self.share.getImageFromPix('logo'))
		self.coreWindow.connect("scroll-event",self.__printEvent)
		self.coreWindow.connect("key-press-event",self.onWindowCoreEvent)

		self.interface.coreWindow = self.coreWindow

		# Gets play button and menu play item from glade template
		self.PlayButton   = xml['ToggleButtonPlay']
		self.interface.playButton =  self.PlayButton
		self.menuItemPlay = xml['MenuItemPlay']

		openremotemitem = xml['open_remote1']
		openremotemitem.connect('activate', lambda widget: openRemote())

		self.Menus = {}

		for i in ('media', 'edit', 'control', 'help'):
			self.Menus["%s" % i] = xml["%s_menu" % i].get_submenu()

		# cdisplaybox is the display gtk-Box
		self.__HBoxCairoDisplay = xml['HBoxCairoDisplay']

		#self.__controlButtons = christineButtons()
		#self.__HBoxCairoDisplay.pack_start(self.__controlButtons,
		#								False, False, 0)
		#self.__controlButtons.show()

		# Create the display and attach it to the main window
		self.__Display = Display()
		self.__Display.connect('value-changed', self.onScaleChanged)
		self.__HBoxCairoDisplay.pack_start(self.__Display, True, True, 0)
		self.__Display.show()

		# Create the library by calling to libs_christine.library class
		self.mainLibrary  = library()
		lastSourceUsed = self.__christineGconf.get('backend/last_source')
		if not lastSourceUsed:
			lastSourceUsed = 'music'
		self.mainLibrary.loadLibrary(lastSourceUsed)
		del lastSourceUsed

		self.mainLibrary.tv.show()

		# Models in the library are assigned to class variables
		self.__LibraryModel       = self.mainLibrary.tv.get_model()
		self.__LibraryCurrentIter = self.mainLibrary.model.get_iter_first()

		self.mainLibrary.scroll
		self.libraryVBox = xml['libraryVBox']
		self.libraryVBox.pack_start(self.mainLibrary.scroll, True, True)
		self.__VBoxVideo = xml['VBoxVideo']

		#self.mainLibray.scroll.add(self.mainLibrary.tv)

		self.Queue = queue()

		self.VBoxList.pack_start(self.Queue.scroll, False, False, 2)
		self.Queue.tv.connect('row-activated',   self.Queue.itemActivated)

		sourcesList = sources_list()
		self.__VBoxList.pack_start(sourcesList.vbox)
		sourcesList.treeview.connect('row-activated',
				self.__srcListRowActivated)
		sourcesList.vbox.show_all()

		self.__ControlButton = xml['control_button']

		self.__MenuItemShuffle = xml['MenuItemShuffle']
		self.__MenuItemShuffle.set_active(self.__christineGconf.getBool('control/shuffle'))

		self.__MenuItemShuffle.connect('toggled',
			lambda widget: self.__christineGconf.setValue('control/shuffle',
			widget.get_active()))

		self.__christineGconf.notifyAdd('control/shuffle',
			self.__christineGconf.toggleWidget,
			self.__MenuItemShuffle)

		self.__ControlRepeat = xml['repeat']
		self.__ControlRepeat.set_active(self.__christineGconf.getBool('control/repeat'))

		self.__ControlRepeat.connect('toggled',
			lambda widget: self.__christineGconf.setValue('control/repeat',
			widget.get_active()))

		self.__christineGconf.notifyAdd('control/repeat',
			self.__christineGconf.toggleWidget,
			self.__ControlRepeat)

		self.__BothSr = xml['both_sr']
		self.__NoneSr = xml['none_sr']

		self.__MenuItemVisualMode = xml['MenuItemVisualMode']
		self.__MenuItemVisualMode.set_active(self.__christineGconf.getBool('ui/visualization'))

		self.visualModePlayer()

		self.__MenuItemSmallView.set_active(self.__christineGconf.getBool('ui/small_view'))
		self.toggleViewSmall(self.__MenuItemSmallView)

		translateMenuItem = xml['translateThisApp']
		URL = 'https://translations.launchpad.net/christine/0.1/'
		translateMenuItem.connect('activate', lambda widget: webbrowser.open(URL))

		reportaBug = xml['reportABug']
		URL = BUGURL
		reportaBug.connect('activate', lambda widget: webbrowser.open(URL))

		self.__HBoxToolBoxContainer = xml['HBoxToolBoxContainer']
		self.__HBoxToolBoxContainer.set_property('events',gtk.gdk.ENTER_NOTIFY|gtk.gdk.SCROLL_MASK)
		self.__HBoxToolBoxContainer.connect("scroll-event",self.__printEvent)

		self.__HBoxButtonBox		= xml['HBoxButtonBox']
		self.__HBoxButtonBox.set_property('events',gtk.gdk.ENTER_NOTIFY|gtk.gdk.SCROLL_MASK)
		self.__HBoxButtonBox.connect('scroll-event',self.__printEvent)

		self.__HScaleVolume         = xml['HScaleVolume']
		self.__HScaleVolume.connect("scroll-event",self.__printEvent)

		volume = self.__christineGconf.getFloat('control/volume')
		if (volume):
			self.__HScaleVolume.set_value(volume)
		else:
			self.__HScaleVolume.set_value(0.8)

		self.__HBoxToolBoxContainerMini = self.__HBoxToolBoxContainer
		self.jumpToPlaying(path = self.__christineGconf.getString('backend/last_played'))

	def __srcListRowActivated(self, treeview, path, column):
		model = treeview.get_model()
		fname = model.get_value(model.get_iter(path),
				LIST_NAME)
		self.mainLibrary.loadLibrary(fname)
		self.__christineGconf.setValue('backend/last_source', fname)

	def deleteFileFromDisk(self, widget):
		"""
		Delete file from disk
		"""
		selection     = self.mainLibrary.tv.get_selection()
		(model, iter) = selection.get_selected()
		iter          = iter

		self.mainLibrary.delete_from_disk(iter)

	def removeFromLibrary(self, widget = None):
		"""
		Remove file from library
		"""
		selection     = self.mainLibrary.tv.get_selection()
		(model, iter) = selection.get_selected()
		name,path     = model.get(iter, NAME, PATH)
		if self.__christineGconf.getString("backend/last_played") == path:
			self.__christineGconf.setValue("backend/last_played","")
		self.mainLibrary.remove(iter)
		#self.mainLibrary.save()


	def setLocation(self, filename):
		"""
		Set the location in the player and
		perform some other required actions
		"""
		self.__StatePlaying = False
		self.__IterNatural  = None
		print filename
		# current iter is a temporal variable
		# that will hold a gtk.TreeIter
		# should be setted to None
		# before using it
		self.__LibraryCurrentIter = None

		self.__Player.stop()
		self.__LibraryCurrentIter = self.mainLibrary.model.basemodel.search_iter_on_column(self.__Player.getLocation(), PATH)

		if (self.__LibraryCurrentIter != None):
			pix = self.share.getImageFromPix('blank')
			pix = pix.scale_simple(20, 20,
					gtk.gdk.INTERP_BILINEAR)
			path = self.mainLibrary.model.basemodel.get_path(self.__LibraryCurrentIter)
			self.mainLibrary.set(path, PIX, pix)
			self.__IterNatural = self.__LibraryCurrentIter

		# Search for the item in the library.
		# if it exists then set it in the "backend/last_played"
		# entry in gconf to be able to select it in the next
		# christine start-up (and other functions) and
		#self.__LibraryCurrentIter = None
		#self.__LibraryCurrentIter = self.mainLibrary.model.basemodel.search_iter_on_column(filename, PATH)
		self.IterCurrentPlaying = self.__LibraryCurrentIter
		self.IterCurrentPlaying = self.mainLibrary.model.getIterValid(self.IterCurrentPlaying)
		if self.IterCurrentPlaying != None:
			if self.mainLibrary.model.basemodel.iter_is_valid(self.IterCurrentPlaying):
				self.IterCurrentPlaying = self.__LibraryCurrentIter
		if (self.IterCurrentPlaying != None):
			if (self.mainLibrary.Exists(filename)):
				count = self.mainLibrary.model.getValue(self.IterCurrentPlaying, PLAY_COUNT)
				self.mainLibrary.model.setValues(self.IterCurrentPlaying, PLAY_COUNT, count + 1)
				self.__IterNatural = self.IterCurrentPlaying

				#self.mainLibrary.save()
				self.__LastPlayed.append(filename)
				self.__christineGconf.setValue('backend/last_played', filename)
		self.__Player.setLocation(filename)
		name = os.path.split(filename)[-1]
		self.__Display.setSong(name)
		# enable the stream-length for the current song.
		# this will be stopped when we get the length
		gobject.idle_add(self.__streamLength)
		# if we can't get the length, in more than 20
		# times in the same song, then, jump to the
		# next song
		if (self.__LocationCount > 10):
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
		self.__christineGconf.setValue('control/volume', value)

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
		self.__christineGconf.setValue('ui/small_view', active)

		if (active):
			self.__HPanedListsBox.hide()
			self.HBoxSearch.hide()

			self.coreWindowSize = self.coreWindow.get_size()
			self.coreWindow.unmaximize()
			self.coreWindow.resize(10, 10)
			self.coreWindow.set_resizable(False)
		else:
			try:
				(w, h) = self.coreWindowSize
			except:
				(w, h) = (800, 480)

			self.__HPanedListsBox.show()
			self.HBoxSearch.show()
			self.coreWindow.resize(w, h)
			self.coreWindow.set_resizable(True)

	def toggleVisualization(self, widget):
		"""
		This show/hide the visualization
		"""
		self.__christineGconf.setValue('ui/visualization', widget.get_active())
		self.visualModePlayer()

		# Be shure that we are not in small view mode.
		if ((self.__MenuItemSmallView.get_active()) and (not widget.get_active())):
			self.toggleViewSmall(self.__MenuItemSmallView)
		self.__Player.setVisualization(widget.get_active())

	def toggleFullScreen(self, widget = None):
		"""
		Set the full Screen mode
		"""
		# Only if we are not in FullScreen and we are playing a video.
		# FIXME: We must enable the full screen if christine has
		#        visualization enabled
		if (not self.__IsFullScreen):
			if ((self.__Player.isVideo()) or (self.__christineGconf.getBool('ui/visualization'))):
				self.coreWindow.fullscreen()
				self.mainLibray.scroll.set_size_request(0,0)
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
			if ((not self.__Player.isVideo()) and (not self.__christineGconf.getBool('ui/visualization'))):
				self.__Player.hide()
			self.mainLibray.scroll.set_size_request(200,200)
			self.__VBoxList.set_size_request(150,0)

			self.coreWindow.unfullscreen()
			self.__IsFullScreen = False

	def onWindowCoreEvent(self, player, event):
		"""
		Handler for the events in the window
		"""
		if (event.type == gtk.gdk.KEY_PRESS):
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
#===============================================================================
#		if not self.EntrySearch.get_text().lower():
#			self.jumpToPlaying()
#===============================================================================
		self.__lastTypeTime = time.time()
		gobject.timeout_add(500,self.__searchTimer)

	def __searchTimer(self):
		diff = time.time() - self.__lastTypeTime
		if diff > 0.3 and diff < 1:
			self.mainLibrary.model.TextToSearch = self.EntrySearch.get_text().lower() 
			self.mainLibrary.model.refilter()
			self.jumpToPlaying()
			return False
		if diff > 1:
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
			self.__LibraryCurrentIter = self.mainLibrary.model.basemodel.search_iter_on_column(
										self.__christineGconf.getString('backend/last_played'), PATH)
			if self.__LibraryCurrentIter != None:
				path = self.__LibraryModel.get_path(self.__LibraryCurrentIter)

				if (path > 0):
					path = (path[0] -1,)
				elif (path[0] > -1):
					iter     = self.__LibraryModel.get_iter(path)
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
		#import pdb
		#pdb.set_trace()
		iter  = model.get_iter_first()

		if (type(iter) == gtk.TreeIter):
			self.interface.Queue.scroll.show()
			location = self.Queue.model.get_value(iter,PATH)
			self.setLocation(location)
			self.__LibraryCurrentIter = None
			self.jumpToPlaying()
			self.Queue.remove(iter)
			self.Queue.save()
			self.PlayButton.set_active(False)
			self.PlayButton.set_active(True)
		else:
			self.interface.Queue.scroll.hide()
			if (self.__MenuItemShuffle.get_active()):
				Elements = len (self.__LibraryModel) - 1
				if Elements < 0:
					return True
				randompath = ((int(Elements * random.random())),)
				filename = self.__LibraryModel[randompath][PATH]
				if (not filename in self.__LastPlayed) or \
						(self.__christineGconf.getBool('control/repeat')) and filename:
						self.setLocation(filename)
						self.PlayButton.set_active(False)
						self.PlayButton.set_active(True)
				else:
					self.getNextInList()
					self.PlayButton.set_active(False)
					self.PlayButton.set_active(True)
			else:
				self.getNextInList()

	def getNextInList(self):
		"""
		Gets the next item in list
		"""
		path = self.__christineGconf.getString('backend/last_played')

		if (path == None):
			filename = self.__christineGconf.getString('backend/last_played')
			self.__LibraryCurrentIter = self.mainLibrary.model.basemodel.search_iter_on_column(filename, PATH)
			#self.__Player.getLocation()
			if (self.__LibraryCurrentIter == None):
				iter     = self.__LibraryModel.get_iter_first()
				filename = self.mainLibrary.model.getValue(iter, PATH)
				self.IterCurrentPlaying = iter

			self.setLocation(filename)
		else:
			self.__LibraryCurrentIter = None
			self.__LibraryCurrentIter = self.mainLibrary.model.basemodel.search_iter_on_column(path, PATH)
			if (self.__LibraryCurrentIter != None):
				iter = self.__LibraryModel.iter_next(self.__LibraryCurrentIter)
			else:
				iter = self.__LibraryModel.get_iter_first()

			self.IterCurrentPlaying = iter
			try:
				self.setLocation(self.mainLibrary.model.getValue(iter, PATH))
				#niter = iter
				self.PlayButton.set_active(False)
				self.PlayButton.set_active(True)
			except:
				self.setScale('', '', b = 0)
				self.setLocation(path)
				self.PlayButton.set_active(False)

	def __SearchByPath(self, model, path, iter, location):
		"""
		search location in the model, if it found it then it will
		store the iter where it was found in self.__LibraryCurrentIter
		"""
		mlocation = model[path][PATH]
		if (mlocation == location):
			self.__LibraryCurrentIter = path
			return True

	def onScaleChanged(self, scale, a, value = None):
		"""
		Callback on the value changed signal on position scale
		"""
		value = (int(self.__Display.value * self.__TimeTotal) / gst.SECOND)
		total = self.__TimeTotal*gst.SECOND

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

	def jumpToPlaying(self, widget = None, path = None):
		"""
		This method jumps and select the file
		specified in the path.
		If path is not specified then try to
		select the playing one
		"""
		if not isinstance(path, str) or not path:
			location = self.__Player.getLocation()
		else:
			location = path
		self.__LibraryCurrentIter = self.mainLibrary.model.basemodel.search_iter_on_column(location, PATH)

		if self.__LibraryCurrentIter != None:
			if self.__StatePlaying:
				iter = self.__LibraryCurrentIter
				pix  = self.share.getImageFromPix('sound')
				pix  = pix.scale_simple(20, 20,
						gtk.gdk.INTERP_BILINEAR)
				self.mainLibrary.set(iter, PIX, pix)
		iter = self.mainLibrary.search(location, PATH)
		#iter = self.mainLibrary.model.convert_natural_iter_to_iter(self.__LibraryCurrentIter)
		if iter != None:
			self.IterCurrentPlaying = iter
			npath = self.mainLibrary.model.sorted_path(iter)
			if (npath != None):
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
		if (self.__TimeTotal == 0):
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
		if (response == gtk.RESPONSE_OK):
			time = ((mins_scale.get_value() * 60) + secs_scale.get_value())
			if (time > self.__TimeTotal):
				time = self.__TimeTotal
			self.__Player.seekTo(time)

	def jumpToOkClicked(self, widget, event, button):
		"""
		Jumpo to Accept button
		"""
		if (event.keyval in (gtk.gdk.keyval_from_name('Return'),
					gtk.gdk.keyval_from_name('KP_Enter'))):
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
	#               libraty stuff begins               #
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
		uri = self.__christineGconf.getString("ui/LastFolder")
		if uri:
			fs.set_uri(uri)
		fs.set_icon(self.share.getImageFromPix('logo'))
		response = fs.run()
		files    = fs.get_filenames()
		fs.destroy()
		if (response == gtk.RESPONSE_OK):
			self.addFiles(files = files, queue = queue)
			path = os.path.join(os.path.split(files[0])[:-1])[0]
			self.__christineGconf.setValue("ui/LastFolder",path)

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
		uri = self.__christineGconf.getString("ui/LastFolder")
		if uri:
			ds.set_uri(uri)
		ds.set_icon(self.share.getImageFromPix('logo'))
		response  = ds.run()
		filenames = ds.get_filenames()
		if (response == gtk.RESPONSE_OK):
			self.__christineGconf.setValue("ui/LastFolder",filenames[0])
			ds.destroy()
			for i in filenames:
				if (walk.get_active()):
					self.addDirectories(i)
				else:
					files = [os.path.join(i, k) \
					for k in os.listdir(i) if os.path.isfile(os.path.join(i, k))]
					if (len(files) > 0):
						self.addFiles(files = files)
			#self.mainLibrary.save()
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
		for i in files:
			ext = i.split('.').pop()
			if (ext in self.__christineGconf.getString('backend/allowed_files').split(',')):
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
		gobject.timeout_add(100, self.__walkProgressPulse,progress)
		response = dialog.run()
		if response:
			self.__walking = False
		dialog.destroy()

	def __walkProgressPulse(self, progress):
		progress.pulse()
		return True

	def __walkDirectories(self, a, f, filenames, label, dialog):
		if not self.__walking:
			return False
		try:
			(dirpath, dirnames, files) = a.next()
			del dirnames
			filenames.append([dirpath, files])
			try:
				npath = u'%s'%dirpath.decode('latin-1')
				npath = u'%s'%npath.encode('latin-1')
			except Exception, e:
				return True
			label.set_text('Exploring %s'%npath)
			for path in filenames[-1][1]:
				ext    = path.split('.').pop().lower()
				exists = os.path.join(filenames[-1][0], path) in self.f
				if ext in self.__christineGconf.getString('backend/allowed_files').split(',') and not exists:
					f.append(os.path.join(filenames[-1][0],path))
		except StopIteration:
			dialog.destroy()
			if (len(f) > 0):
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
		#c = time.time()
		if len(self.__FilesToAdd) > 0:
			d,m = divmod(len(library.model.basemodel), 500)
			new_file = self.__FilesToAdd.pop()
			library.add(new_file)
			if m == 0:
				library.save()
			self.__updateAddProgressBar(new_file)
		else:
			library.save()
			self.__AddWindow.destroy()
			return False
		#print time.time() -c
		return True

	def __updateAddProgressBar(self, file):
		length = len(self.__FilesToAdd)
		if (length > 0):
			self.__Percentage = (1 - (length / float(self.__TimeTotalNFiles)))
		else:
			self.__Percentage = 1
		if (self.__Percentage > 1.0):
			self.__Percentage = 1.0
		# Setting the value and text in the progressbar
		self.__AddProgress.set_fraction(self.__Percentage)
		rest = (self.__TimeTotalNFiles - length)
		text = "%02d/%02d" % (rest, self.__TimeTotalNFiles)
		self.__AddProgress.set_text(text)
		self.__AddFileLabel.set_text(os.path.split(file)[1])
		return length

	def addFiles(self, widget = None, files = None, queue = False):
		"""
		Add files to the library or to the queue
		"""
		XML = self.share.getTemplate('addFiles')
		XML.signal_autoconnect(self)

		self.__AddWindow       = XML['WindowCore']
		self.__AddProgress     = XML['progressbar']
		self.__AddCloseButton  = XML['close']
		self.__AddFileLabel    = XML['file_label']
		self.__AddFileLabel.set_text('None')
		self.__AddCloseButton.connect("clicked",self.importCancel)

		self.__AddCloseButton.grab_add()
		# Be sure that we are working with a list of files
		if not isinstance(files, list):
			raise TypeError, "files must be List, got %s" % type(files)
		files.reverse()
		# Global variable to save temporal files and paths
		self.__FilesToAdd = []
		self.__Paths      = []
		self.mainLibrary.model.basemodel.foreach(self.getPaths)
		for i in files:
			ext    = i.split('.').pop().lower()
			if (not i in self.__Paths) and \
					(ext in self.__christineGconf.getString('backend/allowed_files').split(',')):
				self.__FilesToAdd.append(i)
		self.__Percentage      = 0
		self.__TimeTotalNFiles = len(self.__FilesToAdd)
		self.__addFile(queue=queue)

	def getPaths(self, model, path, iter):
		"""
		Gets path from
		"""
		self.__Paths.append(model.get_value(iter, PATH))

	def importCancel(self, widget):
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
		elif (type_file == gst.MESSAGE_ELEMENT):
			self.__Player.emitExpose()
			return True
		return True

	def checkTimeOnMedia(self):
		"""
		Update the time showed in the player
		"""
		try:
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
		if (self.__Player.getLocation().split(':')[0] == 'http'):
			return True
		try:
			self.__TimeTotal = self.__Player.query_duration(gst.FORMAT_TIME)[0]
			ts               = (self.__TimeTotal / gst.SECOND)
			text             = "%02d:%02d" % divmod(ts, 60)
			self.__ErrorStreamCount = 0
			iter = self.__LibraryCurrentIter
			if (iter is not None):
				time= self.mainLibrary.model.get_value(iter, TIME)
				if (time != text):
					self.mainLibrary.updateData(self.__Player.getLocation(),
								time=text)
			return False
		except gst.QueryError:
			self.__ErrorStreamCount += 1
			if (self.__ErrorStreamCount > 10):
				self.setLocation(self.__Player.getLocation())
				self.PlayButton.set_active(False)
				self.PlayButton.set_active(True)

			return True

	def setTags(self, widget = "", b = ""):
		"""
		This method fetchs teh data from the song/media in the player.
		Then, ask to the library to update the values on it.
		"""
		#if not self.mainLibrary.Exists(self.__Player.getLocation()):
		#	return False
		title     = self.__Player.getTag('title').replace('_', ' ')
		artist    = self.__Player.getTag('artist')
		album     = self.__Player.getTag('album')
		genre     = self.__Player.getTag('genre')
		type_file = self.__Player.getType()

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
		if type(track_number) == type(""):
			if track_number.isdigit():
				track_number = int(track_number)
			else:
				track_number = 0

		if (title == ''):
			title = os.path.split(self.__Player.getLocation())[1]
			title = '.'.join(title.split('.')[:-1])

		# stript_XML_entities is a method inherited from gtk_misc
		tooltext = title
		title    = self.strip_XML_entities(title)

		# Sets window title, which it will be our current song :-)
		self.coreWindow.set_title("%s - Christine" % title)

		notify_text = "<big>%s</big>\n" % title

		# Show or hide deppending if there are something
		# to show or hide
		if (artist != ''):
			notify_text += " by <big>%s</big>\n" % artist
			tooltext    += "\nby %s" % artist

		if (album != ''):
			notify_text += " from <big>%s</big>" % album
			tooltext    += "\nfrom %s" % album

		search = '.'.join([title,artist, album, genre, type_file])

		self.mainLibrary.updateData(self.__Player.getLocation(),
								title=title,
								album= album,
								artist=artist,
								track_number=track_number,
								search=search,
								genre=genre)

		if ((PYNOTIFY) and (self.__christineGconf.getBool('ui/show_pynotify'))):
			try:
				self.__Notify.close()
			except:
				pass
			pixmap = self.share.getImage('trayicon')
			self.__Notify = pynotify.Notification('christine', '',pixmap)

			if (self.__christineGconf.getBool('ui/show_in_notification_area')):
				try:
					self.__Notify.attach_to_status_icon(self.interface.TrayIcon.TrayIcon)
				except:
					pass
				self.interface.TrayIcon.TrayIcon.set_tooltip(tooltext)

			#self.__Notify.set_timeout(3000)

			self.__Notify.set_property('body', notify_text)
			self.__Notify.show()
		self.interface.TrayIcon.TrayIcon.set_tooltip(title + ' - ' + artist)
		if tooltext != '':
			self.__Display.setSong(tooltext.replace('\n', ' '))
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
			self.__HBoxPlayer.show_all()
		else:
			if (self.__christineGconf.getBool('ui/visualization') and isPlaying):
				self.__HBoxPlayer.show_all()
			else:
				self.__HBoxPlayer.hide()

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
		guiAbout()

	def showGtkPreferences(self, widget):
		"""
		Show the preferences dialog
		"""
		guiPreferences()

	def quitGtk(self, widget = None):
		self.__Player.stop()
		pidfile = 	os.path.join(os.environ['HOME'],'.christine',
								'christine.pid')
		if os.path.exists(pidfile):
			os.unlink(pidfile)
		gtk.main_quit()

	def runGtk(self):
		"""
		GTK application running
		"""
		gtk.main()

