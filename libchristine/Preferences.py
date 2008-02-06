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
# @category  GTK
# @package   Preferences
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
#from libchristine.ChristineLibrary import *
from libchristine.GtkMisc import GtkMisc
from libchristine.Translator import *
from libchristine.Share import Share
from libchristine.Validator import *
from libchristine.ChristineGConf import ChristineGConf
import gtk
#
# Preferences gtk dialog
#
class guiPreferences(GtkMisc):
	"""
	Preferences gtk dialog
	"""
	
	#
	# Constructor
	#
	def __init__(self):
		"""
		Constructor
		"""
		GtkMisc.__init__(self)

		self.__GConf = ChristineGConf()
		self.__Share = Share()

		self.XML = self.__Share.getTemplate('Preferences')
		self.XML.signal_autoconnect(self)

		self.__AudioSink = self.XML['audiosink']
		self.__AudioSink.connect('changed', self.updateSink, 'audiosink')

		self.__VideoSink = self.XML['videosink']
		self.__VideoSink.connect('changed', self.updateSink, 'videosink')

		self.__FModel    = gtk.ListStore(str)
		self.__FTreeView = self.XML['ftreeview']
		self.__FTreeView.set_model(self.__FModel)

		self.__FAdd = self.XML['fadd']
		self.__FDel = self.XML['fdel']

		self.updateFModel()
		self.__setFColumns()
		self.__GConf.notify_add('/apps/christine/backend/allowed_files',
								lambda a,b,c,d:self.updateFModel())

		self.selectSinks()

		dialog	 = self.XML['WindowCore']
		dialog.set_icon(self.__Share.getImageFromPix('logo'))
		self.setCheckBoxes()
		dialog.run()
		dialog.destroy()

	#
	# Sets columns
	#
	def __setFColumns(self):
		"""
		Sets columns
		"""
		render = gtk.CellRendererText()
		render.set_property('editable', True)
		render.connect('edited', self.onCursorChanged)
		self.__FTreeView.append_column(gtk.TreeViewColumn('Extension', render, text = 0))

	#
	# Saves model
	#
	def __saveFModel(self):
		"""
		Saves Model
		"""
		exts = ','.join([self.__FModel.get_value(k.iter, 0) for k in self.__FModel])
		self.__GConf.setValue('backend/allowed_files', exts)

	#
	#  Callback when cursor change
	#
	def onCursorChanged(self, render, path, value):
		"""
		Callback when cursor change
		"""
		self.__FModel.set_value(self.__FModel.get_iter(path), 0, value)
		self.__saveFModel()

	#
	# Updates model
	#
	def updateFModel(self):
		"""
		Update model
		"""
		self.__FModel.clear()
		extensions = self.__GConf.getString('backend/allowed_files').split(',')
		extensions.sort()

		if (len(extensions) < 1):
			return True

		while (len(extensions) > 0):
			self.__FModel.set(self.__FModel.append(), 0, extensions.pop())

	#
	# Adds extension
	#
	# @param  widget widget
	# @return void
	def addExtension(self, widget):
		"""
		Adds extension
		"""
		self.__FModel.set(self.__FModel.append(), 0, translate('New extension'))
		self.__saveFModel()
	
	#
	# Removes extension
	#
	# @param  widget widget
	# @return void
	def removeExtension(self, widget):
		"""
		Removes extension
		"""
		selection     = self.__FTreeView.get_selection()
		(model, iter) = selection.get_selected()

		if (not isNull(iter)):
			model.remove(iter)
			self.__saveFModel()

	#
	# Selects sinks
	#
	def selectSinks(self):
		"""
		Selects sinks
		"""
		videosink = self.__GConf.getString('backend/videosink')
		audiosink = self.__GConf.getString('backend/audiosink')
		audio_m   = self.__AudioSink.get_model()
		video_m   = self.__VideoSink.get_model()

		a = 0
		for i in audio_m:
			if (i[0] == audiosink):
				self.__AudioSink.set_active(a)
				break

			a += 1

		a = 0
		for i in video_m:
			if (i[0] == videosink):
				self.__VideoSink.set_active(a)
				break

			a += 1
	
	#
	# Update sink
	#
	def updateSink(self, combobox, sink):
		"""
		Updates sink
		"""
		path     = combobox.get_active()
		model    = combobox.get_model()
		selected = model.get_value(model.get_iter(path), 0)
		self.__GConf.setValue('backend/%s' % sink, selected)
	
	#
	# Sets checkboxes
	#
	def setCheckBoxes(self):
		"""
		Sets check boxes
		"""
		self.__Artist = self.XML['artist']
		self.__Artist.set_active(self.__GConf.getBool('ui/show_artist'))
		self.__Artist.connect('toggled', self.__GConf.toggle,'ui/show_artist')

		self.__Album = self.XML['album']
		self.__Album.set_active(self.__GConf.getBool('ui/show_album'))
		self.__Album.connect('toggled',self.__GConf.toggle,'ui/show_album')

		self.__Type = self.XML['type']
		self.__Type.set_active(self.__GConf.getBool('ui/show_type'))
		self.__Type.connect('toggled',self.__GConf.toggle,'ui/show_type')

		self.__Length = self.XML['length']
		self.__Length.set_active(self.__GConf.getBool('ui/show_length'))
		self.__Length.connect('toggled',self.__GConf.toggle,'ui/show_length')
	
		self.__TrackNumber = self.XML['track_number']
		self.__TrackNumber.set_active(self.__GConf.getBool('ui/show_tn'))
		self.__TrackNumber.connect('toggled',self.__GConf.toggle,'ui/show_tn')
		
		self.__PlayCount = self.XML['play_count']
		self.__PlayCount.set_active(self.__GConf.getBool('ui/show_play_count'))
		self.__PlayCount.connect('toggled',self.__GConf.toggle,'ui/show_play_count')

		self.__Genre = self.XML['genre']
		self.__Genre.set_active(self.__GConf.getBool('ui/show_genre'))
		self.__Genre.connect('toggled',self.__GConf.toggle,'ui/show_genre')

		self__NotifyArea = self.XML['notification_area']
		self__NotifyArea.set_active(self.__GConf.getBool('ui/show_in_notification_area'))
		self__NotifyArea.connect('toggled',self.__GConf.toggle,'ui/show_in_notification_area')

		self.__LibNotify = self.XML['pynotify']
		self.__LibNotify.set_active(self.__GConf.getBool('ui/show_pynotify'))
		self.__LibNotify.connect('toggled',self.__GConf.toggle,'ui/show_pynotify')
