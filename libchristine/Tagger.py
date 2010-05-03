import os
import mutagen.mp3, mutagen.oggvorbis
from libchristine.pattern.Singleton import Singleton

class Track:
	def setSong(self, song):
		if not isinstance(song, basestring):
			raise ValueError("The first argument must be a string")
		self.Song = song
		self.Title = ""
		self.Artist = ""
		self.Album = ""
		self.Track = "" 
		self.Genre = ""
		self.Length = ""
		self.Bitrate = ""		 
		
	def createDict(self):
		tags = {
				'title'   : self.Title,
				'artist'  : self.Artist,
				'album'   : self.Album,
				'track'   : self.Track,
				'genre'   : self.Genre,
				'length'  : self.Length,
				'bitrate' : self.Bitrate						 
			   }
		return tags
	
	

class MP3Track(Singleton,Track):
	IDS = { "TIT2": "title",
			"TPE1": "artist",
			"TALB": "album",
			"TRCK": "track",
			"TDRC": "year",
			"TCON": "genre"
			}
	
	def getTag(self, id3, t):
		if not id3.has_key(t): return ""
		text = str(id3[t])

		text = text.replace("\n", " ").replace("\r", " ")
		return text

	def readTags(self,Song):
		self.setSong(Song)
		try:
			info = mutagen.mp3.MP3(self.Song)
		except :
			self.Title = ''
			self.Artist = ''
			self.Album = ''
			self.Genre = ''
			self.Length = ''
			self.Bitrate = ''
			return self.createDict()

		self.Length = info.info.length
		self.Bitrate = info.info.bitrate
		try:
			id3 = mutagen.id3.ID3(self.Song)
			self.Title = self.getTag(id3, "TIT2")
			self.Artist = self.getTag(id3, "TPE1")
			self.Album = self.getTag(id3, "TALB")
			self.Genre = self.getTag(id3, "TCON")

			try:
				# get track/disc id
				track = self.getTag(id3, "TRCK")
				if track.find('/') > -1:
					(self.Track, self.DiscId) = track.split('/')
					self.Track = int(self.Track)
					self.DiscId = int(self.DiscId)
				else:
					self.Track = int(track)

			except ValueError:
				self.Track = 0
				self.DiscId = 0

			self.Year = self.getTag(id3, "TDRC")

		except:
			pass
		
		return self.createDict()

class OGGTrack(Singleton,Track):
	def getTag(self, f, tag):
		try:
			return unicode(f[tag][0])
		except:
			return ""

	def readTags(self,Song):
		self.setSong(Song)
		try:
			f = mutagen.oggvorbis.OggVorbis(self.Song)
		except mutagen.oggvorbis.OggVorbisHeaderError:
			return

		self.Length = int(f.info.length)
		self.Bitrate = int(f.info.bitrate / 1024)

		self.Artist = self.getTag(f, "artist")
		self.Album = self.getTag(f, "album")
		self.Title = self.getTag(f, "title")
		self.Genre = self.getTag(f, "genre")
		if self.getTag(f,"tracknumber").isdigit():
			self.Track = int(self.getTag(f, "tracknumber"))
		else:
			self.Track = 0
		self.DiscId = self.getTag(f, "tracktotal")
		self.Year = self.getTag(f, "date")
		
		return self.createDict()  

class FakeTrack(Singleton,Track):
	def __init__(self, *args):
		Track.__init__(self, *args)

	def readTags(self,song):
		self.setSong(song)
		return self.createDict()


class Tagger(Singleton):
	def readTags(self, song):
		'''
		Reat the tags of a given file
		@param song:
		'''
		if not isinstance(song, basestring):
			raise TypeError('The first argument must be string, got %s'%type(song))
		ext = song.split('.').pop().lower()
		objects = {'mp3':MP3Track, 'ogg':OGGTrack}
		obj = objects.get(ext, FakeTrack)
		self.Rola = obj() 
		return self.Rola.readTags(song)
	
	def taggify(self, file, msg):
		tags = self.readTags(file)
		for i in tags.keys():
			msg = msg.replace('_%s_'%i, str(tags[i]))
		return msg

