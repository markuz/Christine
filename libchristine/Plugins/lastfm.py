# -*- coding: utf-8 -*-
#
# pylast - A Python interface to the Last.fm API.
# Copyright (C) 2008-2009  Amr Hassan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#
# http://code.google.com/p/pylast/




import md5
import urllib2
import thread
import os
from libchristine.Plugins.plugin_base import plugin_base
from libchristine.Share import Share
from libchristine.Tagger import Tagger
from libchristine.globalvars import USERDIR
from libchristine.c3rdparty.pylast import *
import gtk
import webbrowser


APIKEY = '0da3b11c97759f044bd4223dda212daa'
SECRET = 'b8c00f5548c053033b89633d1004d059'


class lastfm(plugin_base):
	def __init__(self):
		plugin_base.__init__(self)
		self.tagger = Tagger()
		self.name = 'Lastfm'
		self.description = 'Enables the last.fm interaction'
		self.configurable = True #If christine should ask for the config dialog
		self.Share = Share()
		if not self.christineConf.configParser.has_section('lastfm'):
			self.christineConf.configParser.add_section('lastfm')
		self.christineConf.notifyAdd('backend/last_played', self.postMessage)

	def configure(self):
		'''
		This method will be called in the christine plugins preferences
		tab when the preferences button get pressed
		'''
		xml = self.Share.getTemplate('plugin_lastfm_main')
		dialog = xml['dialog']
		vbox = xml['vbox']
		autorizebutton = xml['authbuton']
		autorizebutton.connect('clicked', self.__send_auth_request)
		fsd = xml['fetchsessiondata']
		fsd.connect('clicked', self.__fetch_session_data)
		response = dialog.run()
		if response:
			pass
		dialog.destroy()

	def get_active(self):
		return self.christineConf.getBool('lastfm/enabled')

	def set_active(self, value):
		return self.christineConf.setValue('lastfm/enabled', value)


	def __send_auth_request(self, button):
		sessiong = SessionGenerator()
		self.token = sessiong.getToken()	
		url = sessiong.getAuthURL(self.token)
		webbrowser.open(url)
		button.set_text()

	def	__fetch_session_data(self, button):
		sessiong = SessionGenerator()
		data = sessiong.getSessionData(self.token)
		if data:
			self.christineConf.setValue('lastfm/name',data['name'])
			self.christineConf.setValue('lastfm/key',data['key'])
			self.christineConf.setValue('lastfm/subscriber',data['subscriber'])
	
	def postMessage(self, *args):
		'''
		Agrega la cancion que se esta tocando al playlist por defecto
		'''
		if not self.active:
			return
		file = self.christineConf.getString('backend/last_played')
		tags =  self.tagger.readTags(file)
		for key in ('artist','title'):
			if not tags[key]:
				pass
		APIKEY = '0da3b11c97759f044bd4223dda212daa'
		SECRET = 'b8c00f5548c053033b89633d1004d059'
		sessionkey = self.christineConf.getString('lastfm/key')
		username = self.christineConf.getString('lastfm/name')

		user = User(username, APIKEY, SECRET, sessionkey)

		track = Track(tags['artist'], tags['title'], APIKEY, SECRET, sessionkey)
		playlists = user.getPlaylists()
		if playlists:
			thread.start_new(playlists[0].addTrack, (track,))
	
	active = property(get_active, set_active, None,
					'Determine if the plugin is active or inactive')

