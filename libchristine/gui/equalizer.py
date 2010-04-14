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
# @package   Player
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2010 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import gtk
from libchristine.ChristineCore import ChristineCore
from libchristine.gui.GtkMisc import GtkMisc
from libchristine.Share import Share
import gobject

class equalizer(gobject.GObject,GtkMisc):
	__gsignals__= {
				'close' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				}
	def __init__(self):
		gobject.GObject.__init__(self)
		GtkMisc.__init__(self)
		self.core = ChristineCore()
		#Set the adjustment
		#Load the template
		share = Share()
		xml = share.getTemplate('equalizer','topWidget')
		self.topWidget = xml['topWidget']
		closebtn = xml['closebutton']
		closebtn.connect('clicked', self.emitclose)
		self.preset_cb = xml['preset_cb']
		model = gtk.ListStore(str)
		self.preset_cb.set_model(model)
		cell = gtk.CellRendererText()
		self.preset_cb.pack_start(cell, True)
		self.preset_cb.add_attribute(cell, 'text',0)
		self.preset_cb.connect('changed', self._do_load_preset)
		presets = list(self.core.Player.get_preset_names())
		presets.append('neutral')
		presets.sort()
		for preset in presets:
			iter = model.append()
			model.set(iter, 0,preset)
			
		for i in range(10):
			wname = 'band%d'%i
			widget = xml[wname]
			adjustment = gtk.Adjustment(value=-24, lower=-24, upper=12)
			widget.set_adjustment(adjustment)
			widget.connect('value-changed', self.__apply_value, self.core, wname)
			widget.set_value(0)
			self.__dict__[wname] = widget
		#Connect the "preset_loaded"
		self.core.Player.connect('preset_loaded', self._do_preset_loaded)
		if len (self.preset_cb.get_model()):
			self.preset_cb.set_active(0)
	
	def __apply_value(self, widget, core, band):
		value = widget.get_value()
		core.Player.set_band_value(band, value)
	
	def _do_preset_loaded(self, player):
		for i in range(10):
			band = "band%d"%i
			widget = getattr(self, band, None)
			#Get the value of the band.
			value = self.core.Player.get_band_value(band)
			widget.set_value(value)
	
	def _do_load_preset(self, combo):
		index = combo.get_active()
		model = combo.get_model()
		value = model.get_value(model.get_iter(index), 0)
		if value == 'neutral':
			for i in range(10):
				widget = getattr(self, "band%d"%i, None)
				if not widget: continue
				widget.set_value(0)
			return
		self.core.Player.load_preset(value)

	def emitclose(self, button):
		self.emit('close')

