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
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2010 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
from libchristine.christineConf import christineConf
from libchristine.Events import christineEvents
from libchristine.Validator import isFile
from globalvars import CHRISTINE_VIDEO_EXT
from libchristine.Logger import LoggerManager
from libchristine.ui import interface
from libchristine.envelopes import deprecated
import gst
import gtk
import gobject
import os


BORDER_WIDTH = 0

#
# Player for manager play files
#
class Player(gtk.DrawingArea, object):
	"""
	Player for manage play files
	"""
	__gsignals__= {
				'player-play' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				'player-pause' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				'player-stop' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				'set-location' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								(gobject.TYPE_PYOBJECT, 
									gobject.TYPE_PYOBJECT)),
				'io-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				'gst-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								(gobject.TYPE_PYOBJECT,)),
				'end-of-stream' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				'buffering' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								(gobject.TYPE_PYOBJECT,)),
				'found-tag' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),
				'preset-loaded' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								tuple()),

				}
	#
	# Constructor
	#
	def __init__(self):
		"""
		 Constructor
		"""
		gtk.DrawingArea.__init__(self)
		self.christineConf   = christineConf()
		self.set_events(gtk.gdk.POINTER_MOTION_MASK |
        gtk.gdk.POINTER_MOTION_HINT_MASK |
        gtk.gdk.EXPOSURE_MASK |
        gtk.gdk.KEY_PRESS_MASK |
        gtk.gdk.KEY_RELEASE_MASK) 
		self.unset_flags(gtk.DOUBLE_BUFFERED)
		self.set_flags(gtk.APP_PAINTABLE)
		self.set_size_request(100,100)
		self.interface = interface()
		self.interface.Player = self
		self.__Logger = LoggerManager().getLogger('Player')
		self.__Logger.info('Starting player')
		self.__Text = ''
		self.location = None
		self.config = christineConf(self)
		self.events = christineEvents()
		self.__ShouldShow = False
		self.__createPlaybin()
		self.connect('expose-event', self.exposeCallback)
		self.bus.add_watch(self.__handlerMessage)
		
	def __createPlaybin(self):
		"""
		Create the playbin
		"""
		self.__Logger.info("Creating the Player")
		self.__PlayBin = self.__elementFactoryMake('playbin')
		self.__elementSetProperty(self.__PlayBin,'delay',
								self.config.getInt('backend/gst_delay'))
		self.play = self.__PlayBin
		self.bus  = self.__PlayBin.get_bus()
		self.getState = self.__PlayBin.get_state
		self.__updateAudioSink()
		self.__updateVideoSink()
		self.__updateAspectRatio()
		self.config.notifyAdd('backend/audiosink',    self.__updateAudioSink)
		self.config.notifyAdd('backend/videosink',    self.__updateVideoSink)
		self.config.notifyAdd('backend/aspect-ratio', self.__updateAspectRatio)
		#self.__updateAudioSink()
		#self.__updateVideoSink()
		active = self.config.getBool("ui/visualization")
		if active: self.setVisualization(False)
		self.setVisualization(active)
		self.__connectSinks()
		self.query_duration = self.__PlayBin.query_duration
		self.query_position = self.__PlayBin.query_position



	def __connectSinks(self):
		"""
		Connect the sinks to tye playbin by setting the sinks as elements in the
		playbin
		"""
		self.__Logger.info("Connecting sinks")
		#self.__elementSetProperty(self.__PlayBin,'audio-sink', self.__AudioSinkPack)
		self.__elementSetProperty(self.__PlayBin,'audio-sink', self.aubin)
		self.__elementSetProperty(self.__PlayBin,'video-sink', self.VideoSink)

	def __updateAudioSink(self, *args):
		"""
		Updates audio sink
		"""
		self.__Logger.info("__updateAudioSink")
		state = self.getState()[1]
		#self.__AudioSinkPack = self.__elementFactoryMake('bin')
		if not self.getLocation() == None:
			self.pause()
		asink = self.config.getString('backend/audiosink')
		self.__AudioSinkPack = self.__elementFactoryMake(asink)
		#self.__AudioSinkPack.add(self.__AudioSink)
		#self.audio_ghost = gst.GhostPad('sink', self.__AudioSink.get_pad('sink'))
		#self.__AudioSinkPack.add_pad(self.audio_ghost)
		if asink == 'alsasink':
			self.__AudioSink.set_property('device', 'default')
		self.__create_equalizer()
		#self.__elementSetProperty(self.__PlayBin,'audio-sink', self.__AudioSinkPack)
		if gst.State(gst.STATE_PLAYING) == state:
			self.playIt()

	

	def __updateVideoSink(self, *args):
		"""
		Updates video sink
		"""
		state = self.getState()[1]
		if self.getLocation() != None:
			self.pause()
		vsink = self.config.getString('backend/videosink')
		self.VideoSink = self.__elementFactoryMake(vsink, 'vsink')
		self.__elementSetProperty(self.__PlayBin,'video-sink', self.VideoSink)
		self.__elementSetProperty(self.VideoSink,'force-aspect-ratio', True)
		self.__elementSetProperty(self.VideoSink,'draw-borders', True)
		if gst.State(gst.STATE_PLAYING) == state:
			self.playIt()
	

	def __updateAspectRatio(self, client = '', cnx_id = '', entry = '', userdata = ''):
		"""
		Updates aspect ratio
		"""
		aspect_ratio = self.config.getString('backend/aspect-ratio')
		if not aspect_ratio == None:
			self.__elementSetProperty(self.VideoSink, 'pixel-aspect-ratio',
									aspect_ratio)

	def __elementFactoryMake(self,element, type= ''):
		'''
		Wrap the gst.element_factory_make, but add logging capabilities

		@param element: element to be created (str)
		'''
		self.__Logger.info("creatign a gst element %s"%element)
		return gst.element_factory_make(element, type)

	def __elementSetProperty(self,element,property,value):
		''' 
		Wrap the self.(element).set_property, but add logging capabilities

		@parame element: gst.Element
		@param property: string Property
		@param value: property value
		'''
		self.__Logger.info("setting property '%s' with value '%s", property,str(value))
		try:
			element.set_property(property,value)
			return True
		except Exception, e:
			self.__Logger.exception(e)

	def exposeCallback(self, window, event):
		"""
		Draw the visualization widget.
		"""
		# Drawing a black background because some
		# GTK themes (clearlooks) don't draw it
		
		if not self.window:
			return False
		w, h = (self.allocation.width, self.allocation.height)
		try:
			self.VideoSink.set_xwindow_id(self.window.xid)
		except:
			pass
		self.__Context = self.window.cairo_create()
		self.__Context.rectangle(BORDER_WIDTH, BORDER_WIDTH,
		                         w - 2 * BORDER_WIDTH,
		                         h - 2 * BORDER_WIDTH)
		self.__Context.clip_preserve()

		self.__Context.set_source_rgba(0,0,0)
		self.__Context.fill_preserve()
		self.__Context.stroke()
		if self.__ShouldShow:
			width = self.getTag('width')
			height = self.getTag('height')
			if not width or not height:
				width, height = 400,200
			self.set_size_request(width, height)
			self.show()
	
	@deprecated
	def setLocation(self, file):
		self.set_location(file)
	
	def set_location(self, file):
		self.Tags = {}
		last_location = self.getLocation()
		self.location = file
		if getattr(self, 'visualizationPlugin', None) != None and \
			os.name != "nt":
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', self.visualizationPlugin)
		if (isFile(file)):
			self.__setState(gst.STATE_READY)
			if os.name == 'nt':
				p = file.split("\\")
				file = "/" + "/".join(p)
			nfile = 'file://' + file
			self.__elementSetProperty(self.__PlayBin,'uri', nfile)
			self.__elementSetProperty(self.__PlayBin, 'suburi', None)
			self.__elementSetProperty(self.__PlayBin, 'subtitle-font-desc', None)
			self.__elementSetProperty(self.__PlayBin, 'subtitle-encoding', None)
			if self.isVideo():
				self.__ShouldShow = True
				self.__elementSetProperty(self.VideoSink,'force-aspect-ratio', True)
				subtitle = '.'.join(file.split('.')[:-1]) + '.srt'
				if os.path.exists(subtitle):
					self.__elementSetProperty(self.__PlayBin, 'suburi', 'file://'+subtitle)
					self.__elementSetProperty(self.__PlayBin, 'subtitle-font-desc', self.config.getString('backend/subtitle_font_desc'))
					self.__elementSetProperty(self.__PlayBin, 'subtitle-encoding', self.config.getString('backend/subtitle_encoding'))
					
		else:
			file = file.replace( "\\'", r"'\''" )
			if file:
				self.__elementSetProperty(self.__PlayBin,'uri', file)
		self.emit('set-location',last_location, self.location)
		self.christineConf.setValue('backend/last_played', self.location)
		self.show()
		self.getType()
		self.exposeCallback(self.window, gtk.gdk.Event(gtk.gdk.EXPOSE))

	def getLocation(self):
		"""
		Gets location
		"""
		return self.location		

	def playIt(self):
		"""
		Play the current song
		"""
		self.__setState(gst.STATE_PLAYING)
		self.emit('player-play')
		self.events.executeEvent('onPlay')

	def pause(self):
		"""
		Pause the current song
		"""
		self.__setState(gst.STATE_PAUSED)
		self.emit('player-pause')

	def stop(self):
		"""
		Stop the current song
		"""
		self.__setState(gst.STATE_NULL)
		self.emit('player-stop')

	def __setState(self,state):
		'''
		Sets the state of the playtin to the state in
		the state param.
		Add loggin capabilites

		@param: state: gst.STATE
		'''
		self.__Logger.info("Setting the state of the Playbin to %s"%repr(state))
		self.__PlayBin.set_state(state)

	def setVisualization(self, active = False):
		"""
		Sets visualization active or desactive
		"""
		self.__Logger.info("Setting visualization to %s"%repr(active))
		if active:
			if os.name == 'nt':
				return True
			self.visualizationPlugin = self.__elementFactoryMake(self.config.getString('backend/vis-plugin'))
			self.__elementSetProperty(self.VideoSink,'force-aspect-ratio', self.isVideo())
			self.__ShouldShow = True
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', 
									self.visualizationPlugin)
			self.show()
		else:
			states = [k for k in self.getState() if isinstance(k, gst._gst.State)]
			if gst.STATE_PLAYING in states :
				location = self.getLocation()
				sec = self.query_duration(gst.FORMAT_TIME)[0]
				self.stop()
				gobject.timeout_add(500, self.__replay, location, sec)
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', None)
			self.__elementSetProperty(self.VideoSink,'force-aspect-ratio', True)
			self.__ShouldShow = False
		return True
	
	def  __replay(self, location, sec):
		self.setLocation(location)
		sec = (sec / gst.SECOND)
		self.playIt()
		self.seekTo(sec)
		return False

	def __do_quit_visualization(self, sec):
		
		return True

	def setVolume(self, volume):
		if (volume < 0):
			volume = 0.0
		elif (volume > 1):
			volume = 1.0
		self.__elementSetProperty(self.__PlayBin,'volume', volume)

	def getTag(self, key):
		"""
		Gets a specific tag
		"""
		try:
			return self.Tags[key]
		except:
			return ""

	def foundTagCallback(self, tags):
		"""
		Callback to found tags
		"""
		if len(tags.keys()):
			for i in tags.keys():
				if tags[i] != None:
					self.Tags[i] = tags[i]
		self.getType()

	def getType(self):
		"""
		Sets file type
		"""
		if self.isVideo():
			result =  'video'
		elif self.isSound():
			result =  'sound'
		else:
			result = 'Unknown'
		return result
			

	def nano2str(self,nanos):
		"""
		Returns a string like 00:00:00.000000
		"""
		ts = (nanos / gst.SECOND)
		str = '%02d:%02d:%02d.%06d' % ((ts / 3600), 
									(ts / 60), (ts % 60), 
									(nanos % gst.SECOND))
		return str

	def seekTo(self, sec):
		"""
		Seek to secs
		"""
		sec = (long(sec) * gst.SECOND)
		self.__PlayBin.seek(1.0,
		        gst.FORMAT_TIME,    gst.SEEK_FLAG_FLUSH,
				gst.SEEK_TYPE_SET,  sec,
				gst.SEEK_TYPE_NONE, -1)

	def isVideo(self):
		"""
		Check if it is video or not
		"""
		if not self.getLocation():
			return False
		ext = self.getLocation().split('.').pop().lower()
		if self.Tags.has_key('video-codec') or ext in CHRISTINE_VIDEO_EXT:
			self.__ShouldShow = True
			return True
		return False

	def isSound(self):
		"""
		Check if it is sound or not
		"""
		if not self.getLocation():
			return False
		ext = self.getLocation().split('.').pop().lower()
		if self.Tags.has_key('audio-codec') or \
			ext in self.config.getString('backend/allowed_files').split(','):
			return True
		else:
			return False

	def __handlerMessage(self, a, b, c = None, d = None):
		"""
		Handle the messages from 
		"""
		type_file = b.type
		if (type_file == gst.MESSAGE_ERROR):
			if not os.path.isfile(self.getLocation()):
				self.emit('io-eror')
			else:
				self.emit('gst-error',b.parse_error()[1])
		if (type_file == gst.MESSAGE_EOS):
			self.emit('end-of-stream')
		elif (type_file == gst.MESSAGE_TAG):
			self.foundTagCallback(b.parse_tag())
			self.emit('found-tag')
		elif (type_file == gst.MESSAGE_BUFFERING):
			percent = b.structure['buffer-percent']
			self.emit('buffering', percent)
		return True

	def __create_equalizer(self):
		'''
		Creates the equalizer element.
		'''
		self.equalizer = self.__elementFactoryMake('equalizer-10bands','eqsink')
		self.aubin = gst.Bin('audio-bin')
		pad = self.equalizer.get_static_pad('src')
		self.aubin.add_pad(gst.GhostPad('src',pad))
		pad = self.equalizer.get_static_pad('sink')
		self.aubin.add_many(self.equalizer, self.__AudioSinkPack)
		self.aubin.add_pad(gst.GhostPad('sink',pad))
		self.equalizer.link(self.__AudioSinkPack)

	def set_band_value(self, band, value):
		'''
		Set the value for the given band,
		@param string band: may be from band0 to band9.
		@param float value: May be from -24 to 12
		'''
		self.__elementSetProperty(self.equalizer, band, value)
	
	def get_band_value(self, band):
		'''
		return the band value
		@param band: from 'band0' to 'band9'
		'''
		return self.equalizer.get_property(band)
	
	def load_preset(self, preset_name):
		'''
		Load a preset from the preset list.
		@param string preset_name: name of the preset
		@emits: preset_loaded
		'''
		if preset_name not in self.get_preset_names():
			return
		result = self.equalizer.load_preset(preset_name)
		self.emit('preset_loaded')
		return result

	def get_preset_names(self):
		'''
		Return preset names obtanined from self.equalizer.get_preset_names()
		'''
		try:
			result =  self.equalizer.get_preset_names()
		except:
			result =  ['ska', 'techno', 'rock', 'reggae', 'pop', 'more treble', 
					'dance', 'soft', 'club', 'party', 'classic', 'more bass', 
					'ballad', 'more bass and treble']
		return result

