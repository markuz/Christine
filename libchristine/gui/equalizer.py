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



class equalizer(GtkMisc):
	def __init__(self):
		GtkMisc.__init__(self)
		self.core = ChristineCore()
		#Set the adjustment
		#Load the template
		share = Share()
		xml = share.getTemplate('equalizer','topWidget')
		self.topWidget = xml['topWidget']
		for i in range(10):
			wname = 'band%d'%i
			print wname
			widget = xml[wname]
			adjustment = gtk.Adjustment(value=-24, lower=-24, upper=12)
			widget.set_adjustment(adjustment)
			widget.set_value(12)
			widget.connect('value-changed', self.__apply_value, self.core, wname)
			self.__dict__[wname] = widget
	
	def __apply_value(self, widget, core, band):
		value = widget.get_value()
		core.Player.set_band_value(band, value)



