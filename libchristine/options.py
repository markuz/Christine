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
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

from optparse import OptionParser
from libchristine.pattern.Singleton import Singleton
from libchristine.globalvars import VERSION
from libchristine.Translator import translate


class options(Singleton):
	def __init__(self):
		'''
		Constructor. Parsea los valores que vienen en sys.argv[1:] y almacena
		los valores en self.options.
		
		Utiliza optparse para parsear las opciones.
		
		Las opciones disponibles son:
		
		self.options.debug (-v , --debug)
		self.options.daemon (-D, --daemon)
		'''
		usage ='%prog [-v --debug]'
		version = '%prog' +VERSION
		parser = OptionParser(usage = usage,version=version)
		parser.add_option("-d","--devel", dest="debug",action='store_true',
                  help=translate("If christine must run in devel mode"))
		parser.add_option("-v","--verbose", dest="verbose",action='store_true',
                  help=translate("Force christine to dump the logs to the stdout"))
		
		self.options, self.args = parser.parse_args()
		
	
