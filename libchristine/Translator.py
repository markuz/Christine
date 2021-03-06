#!/usr/bin/env python
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
# @category  libchristine
# @package   Translator
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import os
import gettext
from libchristine.pattern.Singleton import *
from libchristine.globalvars import DATADIR, PROGRAMNAME

locale_dir = '@datadir@/locale/'
gettext.bindtextdomain('@programname@', locale_dir)
gettext.textdomain('@programname@')

def translate(text):
    return gettext.gettext(text)

__builtins__["_"] = translate

class Translator(Singleton):
    """
    Translator manager
    """
    #
    # Constructor
    #
    def __init__(self):
        """
        Constructor
        """
        self.setName('Translator')

        self.__Path = os.path.join(DATADIR,'locale')

        gettext.bindtextdomain(PROGRAMNAME, self.__Path)
        gettext.textdomain(PROGRAMNAME)

    #
    # Parse text to be translate
    #
    # @param  string text
    # @return string
    def parse(self, text):
        """
        Parse text to be translate
        """
        return gettext.gettext(text)
