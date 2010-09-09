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
# @copyright 2006-2010 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

#
# This module implements the Christine main Windows
#
import gtk
import gobject
from libchristine.ChristineCore import ChristineCore
#from libchristine.pattern.Singleton import Singleton
from libchristine.Share import Share
from libchristine.gui.buttons import next_button, toggle_button, prev_button

core = ChristineCore()

class mainWindow(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.christineConf = core.config
        self.share = Share()
        self.build_gui()
        
    def build_gui(self):
    ####xml = self.share.getTemplate('WindowCore')
    ####self.mainWindow = xml['WindowCore']
    ####width = core.config.getInt('ui/width')
    ####height = core.config.getInt('ui/height')
    ####if not width or not  height:
    ####    width, height = (800,600)
    ####self.mainWindow.set_default_size(width, height)
    #####self.mainWindow.connect("destroy",lambda widget: widget.hide())
    #####self.mainWindow.connect("scroll-event",self.changeVolumeWithScroll)
    #####self.mainWindow.connect("key-press-event",self.onWindowkeyPressEvent)
    #####self.mainWindow.connect('size-allocate', self.__on_corewindow_resized)

    ####self.mainWindow.show_all()
        """
        This method calls most of the common used
        interface descriptors (widgets) from xml.
        Connects them to a callback (if needed) and
        call some other methods to show/hide them.
        """
        xml = self.share.getTemplate('WindowCore')
        xml.signal_autoconnect(self)

        self.__MenuItemSmallView = xml['ViewSmallMenuItem']
        self.__VBoxCore = xml['VBoxCore']
        self.__VBoxCore.set_property('events',gtk.gdk.ENTER_NOTIFY|
                                    gtk.gdk.SCROLL_MASK)
        self.__VBoxCore.connect('scroll-event',self.changeVolumeWithScroll)
        self.mainSpace = xml['mainSpace']
        self.mainSpace.add1(core.Player)

    
        # Calling some widget descriptors with no callback connected "by hand"
        # This interface should not be private.
        #===================================================
        # Public Widgets
        self.MenuBar = xml['MenuBar']
        self.HBoxSearch = xml['HBoxSearch']
        self.EntrySearch = xml['EntrySearch']
        self.EntrySearch.connect('changed',self.search)
        self.EntrySearch.connect('focus-out-event', self.__EntrySearchFocusHandler)
        self.VBoxList       = xml['VBoxList']
        self.HPanedListsBox = xml['HPanedListsBox']

        # Gets window widget from glade template
        self.mainWindow = xml['WindowCore']
        # Uncoment next lines if you want to use RGBA in your theme
        width = self.christineConf.getInt('ui/width')
        height = self.christineConf.getInt('ui/height')
        if not width or not  height:
            width, height = (800,600)
        self.mainWindow.set_default_size(width, height)
        self.mainWindow.connect("destroy",lambda widget: widget.hide())
        #self.mainWindow.connect("scroll-event",self.changeVolumeWithScroll)
        #self.mainWindow.connect("key-press-event",self.onWindowkeyPressEvent)
        #self.mainWindow.connect('size-allocate', self.__on_corewindow_resized)

        self.__HBoxButtonBox = xml['HBoxButtonBox']
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
        URL = 'https://translations.launchpad.net/christine'
        translateMenuItem.connect('activate', lambda widget: webbrowser.open(URL))

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

