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
# @package   About
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2008 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

from libchristine.Share import Share
from libchristine.Translator import translate
from libchristine.globalvars import PROGRAMNAME, VERSION

#
# Manage about GTK dialog
#
class guiAbout:
	"""
	Manange about GTK dialog
	"""

	#
	# Constructor
	#
	def __init__(self):
		"""
		Constructor
		"""
		self.__Share = Share()

		xml   = self.__Share.getTemplate('About')
		self.about = xml['about']
		pix   = self.__Share.getImageFromPix('logo')

		self.about.set_logo(pix)
		self.about.set_name(PROGRAMNAME)
		self.about.set_version(VERSION)
		self.about.set_icon(self.__Share.getImageFromPix('logo'))
		self.about.set_translator_credits(translate('translator-credits'))

	def run(self):
		self.about.run()
		self.about.destroy()
