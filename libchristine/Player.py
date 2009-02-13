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
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
from libchristine.gui.GtkMisc import error
from libchristine.Validator import isNull
from libchristine.christineConf import christineConf
from libchristine.Events import christineEvents
from libchristine.Validator import isFile
from globalvars import CHRISTINE_VIDEO_EXT
from libchristine.Logger import LoggerManager
from libchristine.ui import interface
import gobject
import gst
import gtk
import os
import pygst; pygst.require('0.10')


BORDER_WIDTH = 0

#
# Player for manager play files
#
class Player(gtk.DrawingArea, object):
	"""
	Player for manage play files
	"""
	#
	# Constructor
	#
	def __init__(self):
		"""
		 Constructor
		"""
		gtk.DrawingArea.__init__(self)
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
		self.config = christineConf(self)
		self.events = christineEvents()
		self.__ShouldShow = False
		self.__Type       = 'sound'
		self.__createPlaybin()
		self.connect('expose-event', self.exposeCallback)
		self.connect('key-press-event', self.__set_text)
	
	def __set_text(self, widget, event):
		name = gtk.gdk.keyval_name()
		self.__Text(name)
		
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
		self.__updateAudioSink()
		self.__updateVideoSink()
		self.__updateAspectRatio()
		self.config.notifyAdd('backend/audiosink',    self.__updateAudioSink)
		self.config.notifyAdd('backend/videosink',    self.__updateVideoSink)
		self.config.notifyAdd('backend/aspect-ratio', self.__updateAspectRatio)
		self.__updateAudioSink()
		self.__updateVideoSink()
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
		self.__elementSetProperty(self.__PlayBin,'audio-sink', self.__AudioSinkPack)
		self.__elementSetProperty(self.__PlayBin,'video-sink', self.VideoSink)

	def __updateAudioSink(self, *args):
		"""
		Updates audio sink
		"""
		self.__Logger.info("__updateAudioSink")
		state = self.getState()[1]
		self.__AudioSinkPack = self.__elementFactoryMake('bin')
		if (not isNull(self.getLocation())): self.pause()
		asink = self.config.getString('backend/audiosink')
		self.__AudioSink = self.__elementFactoryMake(asink)
		self.__AudioSinkPack.add(self.__AudioSink)
		self.audio_ghost = gst.GhostPad('sink', self.__AudioSink.get_pad('sink'))
		self.__AudioSinkPack.add_pad(self.audio_ghost)
		self.__elementSetProperty(self.__PlayBin,'audio-sink', self.__AudioSinkPack)
		if (asink == 'alsasink'):
			self.__AudioSink.set_property('device', 'default')
		if (gst.State(gst.STATE_PLAYING) == state):
			self.playIt()

	def __updateVideoSink(self, *args):
		"""
		Updates video sink
		"""
		state = self.getState()[1]
		if (not isNull(self.getLocation())):
			self.pause()
		vsink = self.config.getString('backend/videosink')
		self.VideoSink = self.__elementFactoryMake(vsink)
		self.__elementSetProperty(self.__PlayBin,'video-sink', self.VideoSink)
		if (vsink in ['xvimagesink', 'ximagesink']):
			self.VideoSink.set_property('force-aspect-ratio', True)
		if (gst.State(gst.STATE_PLAYING) == state):
			self.playIt()

	def __updateAspectRatio(self, client = '', cnx_id = '', entry = '', userdata = ''):
		"""
		Updates aspect ratio
		"""
		aspect_ratio = self.config.getString('backend/aspect-ratio')

		if (not isNull(aspect_ratio)):
			self.__elementSetProperty(self.VideoSink, 'pixel-aspect-ratio',
									aspect_ratio)

	def __elementFactoryMake(self,element):
		'''
		Wrap the gst.element_factory_make, but add logging capabilities

		@param element: element to be created (str)
		'''
		self.__Logger.info("creatign a gst element %s"%element)
		return gst.element_factory_make(element)

	def __elementSetProperty(self,element,property,value):
		'''
		Wrap the self.(element).set_property, but add logging capabilities

		@parame element: gst.Element
		@param property: string Property
		@param value: property value
		'''
		self.__Logger.info("setting property '%s' with value '%s",
						property,str(value))
		element.set_property(property,value)

	def emitExpose(self):
		self.exposeCallback(self.window, gtk.gdk.Event(gtk.gdk.EXPOSE))
		return False

	def exposeCallback(self, window, event):
		"""
		Draw the visualization widget.
		"""
		# Drawing a black background because some
		# GTK themes (clearlooks) don't draw it
		w, h = (self.allocation.width, self.allocation.height)
		try:
			self.VideoSink.set_xwindow_id(self.window.xid)
			self.__Context = self.window.cairo_create()
		except Exception, e:
			print 'No hay window para el videoplayer'
			return False

		self.__Context.rectangle(BORDER_WIDTH, BORDER_WIDTH,
		                         w - 2 * BORDER_WIDTH,
		                         h - 2 * BORDER_WIDTH)
		self.__Context.clip()

		self.__Context.rectangle(BORDER_WIDTH, BORDER_WIDTH,
		                         w - 2 * BORDER_WIDTH,
		                         h - 2 * BORDER_WIDTH)

		self.__Context.set_source_rgba(0,0,0)
		self.__Context.fill_preserve()
		self.__Context.set_source_rgb(0,0,0)
		self.__Context.stroke()
		self.__Layout  = self.create_pango_layout(self.__Text)
		(fontw, fonth) = self.__Layout.get_pixel_size()
		self.__Context.move_to(w, (fonth)/2)
		self.__Context.set_source_rgb(1,1,1)
		self.__Layout.set_font_description(self.style.font_desc)
		self.__Context.update_layout(self.__Layout)
		self.__Context.show_layout(self.__Layout)
		if self.__ShouldShow:
			width = self.getTag('width')
			height = self.getTag('height')
			if not width or not height:
				width, height = 400,200
			self.set_size_request(width, height)
			self.show()
	
	def setLocation(self, file):
		self.Tags = {}
		if getattr(self, 'visualizationPlugin', None) is not None:
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', self.visualizationPlugin)
		if (isFile(file)):
			self.__setState(gst.STATE_READY)
			nfile = 'file://' + file
			self.__elementSetProperty(self.__PlayBin,'uri', nfile)
			self.__elementSetProperty(self.__PlayBin, 'suburi', None)
			self.__elementSetProperty(self.__PlayBin, 'subtitle-font-desc', None)
			self.__elementSetProperty(self.__PlayBin, 'subtitle-encoding', None)
			if self.isVideo():
				self.VideoSink.set_property('force-aspect-ratio', True)
				subtitle = '.'.join(file.split('.')[:-1]) + '.srt'
				if os.path.exists(subtitle):
					print 'It does exists!'
					self.__elementSetProperty(self.__PlayBin, 'suburi', 'file://'+subtitle)
					self.__elementSetProperty(self.__PlayBin, 'subtitle-font-desc', 'Lucida Grande 24')
					self.__elementSetProperty(self.__PlayBin, 'subtitle-encoding', 'ISO-8859-1')
					
		else:
			file = file.replace( "\\'", r"'\''" ) + "'"
			if file:
				#if (file.split(':')[0] in ['http', 'dvd', 'vcd']):
				self.__elementSetProperty(self.__PlayBin,'uri', file)
				#else:
				#	self.__elementSetProperty(self.__PlayBin,'uri', file)
		self.show()
		self.getType()
		self.exposeCallback(self.window, gtk.gdk.Event(gtk.gdk.EXPOSE))

	def getLocation(self):
		"""
		Gets location
		"""
		path = self.__PlayBin.get_property('uri')

		if (not isNull(path)):
			if (path.split(':')[0] == 'file'):
				path = path[7:]
			else:
				return path
		else:
			path = None
		return path

	def playIt(self):
		"""
		Seek to secs
		Play the current song
		"""
		self.__setState(gst.STATE_PLAYING)
		self.events.executeEvent('onPlay')

	def pause(self):
		"""
		Pause the current song
		"""
		self.__setState(gst.STATE_PAUSED)

	def stop(self):
		"""
		Stop the current song
		"""
		self.__setState(gst.STATE_NULL)

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
			self.visualizationPlugin = self.__elementFactoryMake(self.config.getString('backend/vis-plugin'))
			self.VideoSink.set_property('force-aspect-ratio', self.isVideo())
			self.__ShouldShow = True
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', 
									self.visualizationPlugin)
			self.show()
		else:
			self.visualizationPlugin = None
			self.VideoSink.set_property('force-aspect-ratio', True)
			self.__ShouldShow = False
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', None)
			del self.visualizationPlugin
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
		if (len(tags.keys()) > 0):
			for i in tags.keys():
				self.Tags[i] = tags[i]
		self.getType()

	def getState(self):
		"""
		Gets current state
		"""
		return self.__PlayBin.get_state()

	def getType(self):
		"""
		Sets file type
		"""
		if (self.isVideo()):
			self.__Type = 'video'
		elif (self.isSound()):
			self.__Type = 'sound'
		else:
			self.__Type = "Unknown"
		return self.__Type

	def nano2str(self,nanos):
		"""
		Returns a string like 00:00:00.000000
		"""
		ts = (nanos / gst.SECOND)
		return '%02d:%02d:%02d.%06d' % ((ts / 3600), (ts / 60), (ts % 60), (nanos % gst.SECOND))

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
		if (isNull(self.getLocation())):
			return False

		ext = self.getLocation().split('.').pop().lower()

		if (('video-codec' in self.Tags.keys()) or (ext in CHRISTINE_VIDEO_EXT)):
			self.__ShouldShow = True
			return True
		else:
			return False

	def isSound(self):
		"""
		Check if it is sound or not
		"""
		if (isNull(self.getLocation())):
			return False

		ext = self.getLocation().split('.').pop().lower()

		if (('audio-codec' in self.Tags.keys()) or
		  	  (ext in self.config.get('backend/allowed_files'))):
			return True
		else:
			return False
