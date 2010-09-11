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

from libchristine.Logger import LoggerManager

class podcastManager(object):
    '''
    This class will manage Christine's podcasts
    '''
    def __init__(self):
        self.__logger = LoggerManager().getLogger('PodcastManager')
    
    def add(self, url):
        '''
        Add a podcast by url.
        Fist check if the podcast is already in the db. if 
        it is then do nothing, else, try to get the podcast
        and parse it.

        @param string url: The url to the podcast.
        @return bool: True if the podcast got it's way to db. or
                    False if not.
        '''
        pass

