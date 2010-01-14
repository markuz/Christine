#! /usr/bin/env python
## Copyright (c) 2006 Marco Antonio Islas Cruz
## <markuz@islascruz.org>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gc
import os
import gtk
import gobject
import pango
import time
import gst
from libchristine.libs_christine import lib_library
from libchristine.gui.GtkMisc import GtkMisc, error
from libchristine.Translator import translate
from libchristine.christineConf import christineConf
from libchristine.Share import Share
from libchristine.Tagger import Tagger
from libchristine.LibraryModel import LibraryModel
from libchristine.globalvars import CHRISTINE_VIDEO_EXT
from libchristine.Logger import LoggerManager
from libchristine.ui import interface
from libchristine.Storage.sqlitedb import sqlite3db
from libchristine.Events import christineEvents

(PATH,NAME,TYPE,PIX,ALBUM,ARTIST,TN,SEARCH,PLAY_COUNT,TIME,GENRE,
HAVE_TAGS) = range(12)

(VPATH,VNAME,VPIX) = range(3)

QUEUE_TARGETS = [('text/plain',0,0),('TEXT', 0, 1),('STRING', 0, 2),
				('COMPOUND_TEXT', 0, 3), ('UTF8_STRING', 0, 4)]

share = Share()
pix =share.getImageFromPix('blank')
pix = pix.scale_simple(20, 20, gtk.gdk.INTERP_BILINEAR)

##
## Since library and queue are more or less the same
## thing. I guess we need to use a base class for
## both lists (and other lists)
##

class libraryBase(GtkMisc):
	def __init__(self):
		'''
		Constructor, load the
		glade ui description for a simple treeview
		and set some class variables
		'''
		self.iters = {}
		self.__FilesToAdd = []
		GtkMisc.__init__(self)
		self.logger = LoggerManager().getLogger('sqldb')
		self.share = Share()
		self.interface = interface()
		self.christineConf   = christineConf()
		self.db = sqlite3db()
		self.tagger = Tagger()
		self.Events = christineEvents()
		self.last_scroll_time = 0
		self.__xml = self.share.getTemplate("TreeViewSources","scrolledwindow")
		self.__xml.signal_autoconnect(self)
		self.gconf = christineConf()
		self.tv = self.__xml["treeview"]
		self.blank_pix = self.share.getImageFromPix("blank")
		self.blank_pix = self.blank_pix.scale_simple(20,20,gtk.gdk.INTERP_BILINEAR)
		self.add_columns()
		self.scroll = self.__xml['scrolledwindow']
		self.scroll.add_events(gtk.gdk.SCROLL_MASK)
		self.scroll.connect('scroll-event', self.__scroll_child)
		self.scroll.drag_dest_set(gtk.DEST_DEFAULT_DROP,
								QUEUE_TARGETS, gtk.gdk.ACTION_COPY)
		self.tv.connect('scroll-event', self.__scroll_child)
		self.tv.drag_source_set(gtk.gdk.BUTTON1_MASK, 
							QUEUE_TARGETS, gtk.gdk.ACTION_COPY)
		self.tv.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                  gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                  QUEUE_TARGETS, gtk.gdk.ACTION_COPY)
		self.scroll.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                  gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                  QUEUE_TARGETS, gtk.gdk.ACTION_COPY)
		self.tv.connect('drag-data-get', self.drag_data_get)
		self.tv.connect('drag-data-received',self.drag_data_received)
	
	def drag_data_received(self, treeview, context, x, y, 
						selection, info, etime):
		self.tv.emit_stop_by_name('drag-data-received')
		data = selection.data
		files = []
		dirs = []
		for url in [k.strip() for k in data.split("\n")]:
			file = url
			if file.lower().startswith('file://'):
				file = self.replace_XML_entities(file[7:])
			if os.path.isdir(file):
				dirs.append(file)
			else:
				files.append(file)
		self.addFiles(files)
		self.importFolder(dirs, True)
		if context.action == gtk.gdk.ACTION_MOVE:
			context.finish(True, True, etime)
			return
		return True
	
	def drag_data_get(self, treeview,drag_context,selection, info, timestamp):
		treeselection = treeview.get_selection()
		model, iter = treeselection.get_selected()
		text = model.get_value(iter, PATH)
		selection.set('text/plain', 8, text)

	def __scroll_child(self, scroll, event):
		if event.type == gtk.gdk.SCROLL:
			self.last_scroll_time = time.time()
			gobject.timeout_add(500, self.check_file_data)
	
	def check_file_data(self, override = False):
		if not override:
			diff = time.time() - self.last_scroll_time
		else:
			diff = 0.6
		if diff > 0.5 and diff < 1 :
			paths = self.tv.get_visible_range()
			if not paths:
				return True
			startpath = paths[0][0]
			endpath = paths[1][0]
			model = self.model.getModel()
			for i in range(startpath, endpath +1):
				if not self.model.iter_is_valid(i): continue
				siter = model.get_iter(i)
				filepath  = self.model.get_value(siter, PATH)
				self.check_single_file_data(filepath)
				while gtk.events_pending():
						gtk.main_iteration_do()
							
		elif diff > 1.5:
			return False
		return True
	
	def check_single_file_data(self, filepath):
		metatags = self.library_lib.get_by_path(filepath)
		if metatags == None:
			return False
		if metatags['have_tags'] == 1:
			return False
		self.logger.info('I didn\'t find the title tag for %s', filepath)
		self.logger.debug('metatags: %s',repr(metatags))
		if not metatags['have_tags']: 
			metatags = self.tagger.readTags(filepath)
			track_key = 'track'
		else:
			track_key = 'track_number'
		try:
			tn = int(metatags[track_key])
		except:
			tn = 0
		if not metatags['title']:
			filenamesplit = os.path.split(filepath)[1]
			metatags['title'] = '.'.join(filenamesplit.split('.')[:-1])
		for k,v in metatags.iteritems():
			if isinstance(v, str):
				metatags[k] = self.encode_text(v)
		kwargs = {"title":metatags['title'],
				"artist":metatags['artist'],
				"album":metatags['album'],
				"track_number": tn, 
				"play_count":0,
				"time":'0:00',
				"genre":metatags['genre'],
				'have_tags':True
				}
		self.updateData(filepath,**kwargs)

	def loadLibrary(self, library):
		'''
		This method loads a library according to its name.
		@param library: name of the library to be loaded.
		'''
		self.tv.set_model(None)
		self.library_name = library
		if getattr(self, "library_lib", False):
			self.library_lib = None
		self.library_lib = lib_library(library)
		self.gen_model()
		self.fillModel()
		self.model.createSubmodels()
		self.tv.set_model(self.model.getModel())

	def gen_model(self):
		'''
		Generates the model
		'''
		if getattr(self, 'model', False):
			self.model.clear()
		else:
			self.model = LibraryModel(
					str, #path
					str, #name
					str, #type
					gtk.gdk.Pixbuf, #Pix
					str, #album
					str, #artist
					int, #Track Number
					str, #search
					int, #play count
					str, #time
					str, #Genre
					bool, # Have tags
					) 
		del self.iters
		gc.collect(2)
		self.iters = {}

	def fillModel(self):
		keys = self.library_lib.keys()
		keys.sort()
		l = self.library_lib
		model = self.model
		tts = model.TextToSearch.lower()
		while keys:
			path = keys.pop(0)
			self.__insert_item(path, l, model, tts)
		self.library_lib.clear()
	
	def __insert_item(self, path,l,model, tts):
		values = l[path]
		#for key, value in values.iteritems():
		#	if isinstance(value,str):
		#		values[key] = self.encode_text(value)
		searchstring = ''.join((values['title'],values['artist'],
							values['album'],values['type']))
		if not tts or searchstring.lower().find(tts) > -1:
			iter = model.append(PATH,path,
				NAME, values['title'],
				SEARCH,searchstring,
				PIX, pix,
				ARTIST,values['artist'],
				ALBUM ,values['album'],
				GENRE ,values['genre'],
				HAVE_TAGS, bool(values['have_tags']),
				TYPE,values['type'],
				TN,values['track_number'],
				PLAY_COUNT ,values['playcount'],
				TIME ,values['time'],
				)
			#gobject.idle_add(self.__set_extras, model, iter, values)
			self.iters[path] = iter

	def __set_extras(self, model, iter, values):
		model.append(
				TYPE,values['type'],
				TN,values['track_number'],
				PLAY_COUNT ,values['playcount'],
				TIME ,values['time'],
				)


	def add(self,file,prepend=False):
		if isinstance(file, tuple):
			file = file[0]
		if file.lower().startswith('file://'):
			file = self.replace_XML_entities(file[7:])
		if not os.path.isfile(file):
			return False
		name = os.path.split(file)[1]
		if isinstance(name,()):
			name = name[0]
		vals = self.db.getItemByPath(file)
		if not vals:
			#tags = self.tagger.readTags(file)
			tags = {}
			tags['title'] = os.path.split(file)[1].split('.')[0]
			tags['album'] =  ''
			tags['artist'] = ''
			tags['track'] = ''
			tags['genre'] = ''
		else:
			tags = {}
			sme = self.strip_XML_entities
			tags['title'] = sme(self.encode_text(vals['title']))
			tags['album'] =  sme(self.encode_text(vals['album']))
			tags['artist'] = sme(self.encode_text(vals['artist']))
			tags['track'] = vals['track_number']
			tags['genre'] = sme(self.encode_text(vals['genre']))

		if tags["title"] == "":
			n = os.path.split(file)[1].split(".")
			tags["title"] = ".".join([k for k in n[:-1]])

		t = "audio"
		if "video-codec" in tags.keys() or \
				os.path.splitext(file)[1][1:] in CHRISTINE_VIDEO_EXT:
			t = "video"
		if not isinstance(tags["track"], int):
			tags["track"] = 0
		name	= tags["title"]
		album	= tags["album"]
		artist	= tags["artist"]
		tn		= tags["track"]

		if prepend:
			func = self.model.prepend
		else:
			func = self.model.append
		iter = func(NAME,name,
				PATH,file,
				PIX,self.blank_pix,
				TYPE,t,
				ALBUM,album,
				ARTIST,artist,
				TN,int(tn),
				SEARCH,",".join([tags["title"],tags["album"],tags["artist"]]),
				PLAY_COUNT,0,
				GENRE,tags["genre"]
				)

		self.library_lib.append(file, {"title":name,
				"type":t,"artist":artist,
				"album":album,
				"track_number":int(tn),
				"playcount":0,
				"time":'0:00',
				"genre":tags['genre'],})

	def remove(self,iter):
		'''
		Remove the selected iter from the library.
		'''
		key = self.model.getValue(iter,PATH)
		value = self.library_lib.remove(key)
		if value:
			self.model.remove(iter)

	def updateData(self, path, **kwargs):
		'''
		This method updates the data in the main library if it can. And
		in the data base.

		@param path:
		@param title:
		@param album:
		@param artist:
		@param track_number:
		@param search:
		@param genre:
		@param play_count:
		@param time:
		'''
		keys = {'title':NAME,
			 	'album':ALBUM,
			 	'artist':ARTIST,
			 	'track_number':TN,
			 	'search':SEARCH,
			 	'play_count':PLAY_COUNT,
			 	'genre':GENRE,
			 	'time':TIME,
			 	'have_tags': HAVE_TAGS,
			 	}
		for key in kwargs:
			value = keys[key]
			iter = self.model.basemodel.search_iter_on_column(path, PATH)
			if not iter:
				return None
			self.model.basemodel.set(iter, value, kwargs[key])
		iter = self.model.basemodel.search_iter_on_column(path, PATH)
		(path, title, artist, album, type,
		track_number, playcount,time, genre,
		have_tags) = self.model.basemodel.get(iter,
												PATH,
												NAME, ARTIST,ALBUM, TYPE,
												TN,PLAY_COUNT, TIME, GENRE,
												HAVE_TAGS)
		self.library_lib.updateItem(path, title=title, artist=artist,
								album=album, type=type, track_number=track_number,
								playcount=playcount,time=time,
								genre=genre,have_tags = have_tags)

	def key_press_handler(self,treeview,event):
		if event.keyval == gtk.gdk.keyval_from_name('Delete'):
			selection = treeview.get_selection()
			model,iter = selection.get_selected()
			name = model.get_value(iter,NAME)
			model.remove(iter)
			self.library_lib.remove(name)

	def Exists(self,filename):
		'''
		Checks if the filename exits in
		the library
		'''
		result = filename in self.library_lib.keys()
		return result

	# Need some help in the next functions
	# They need to be retouched to work fine.

	def add_it(self,treeview,context,x,y,selection,target,timestamp):
		treeview.emit_stop_by_name("drag_data_received")
		drop_info = treeview.get_dest_row_at_pos(x, y)
		if drop_info:
			data = selection.data
			if data.startswith('file://'):
				data = data.replace('file://','').replace('%20',' ')
				data = data.replace('\n','').replace('\r','')
			self.add(data)
		return True

	def delete_from_disk(self,*args):
		'''
		Takes the current selected item and delete it from the path
		'''
		iter = self.tv.get_selection().get_selected()[1]
		if iter == None:
			return
		dialog = self.share.getTemplate("deleteFileFromDisk")["dialog"]
		response = dialog.run()
		path = self.model.getValue(iter,PATH)
		if response == -5:
			try:
				os.unlink(path)
				self.remove(iter)
			except IOError:
				error("cannot delete file: %s"%path)
		dialog.destroy()

	def clear(self):
		self.model.clear()
		self.library_lib.clear()
		self.library_lib.clean_playlist()

	def itemActivated(self,widget, path, iter):
		model    = widget.get_model()
		iter     = model.get_iter(path)
		filename = model.get_value(iter, PATH)
		self.__FileName = filename
		self.interface.coreClass.setLocation(filename)
		self.IterCurrentPlaying = iter
		self.interface.playButton.set_active(False)
		self.interface.playButton.set_active(True)
		
	def set(self, *args):
		'''
		wraper for the self.model.set
		'''
		return self.model.set(*args)
		
	def search(self, *args):
		'''
		wrapper for the self.model.search
		'''
		return self.model.search(*args)
	
	def refilter(self):
		self.loadLibrary(self.library_name)
	
	def get_path(self, *args):
		'''
		wrapper for the self.model.get_path
		'''
		return self.model.get_path(*args)
	
	def iter_next(self, iter):
		return self.model.iter_next(iter)
	
	def iter_is_valid(self, iter):
		return self.model.iter_is_valid(iter)


	def importFolder(self, filenames, walk):
		"""
		This is the 'simple' way to import folders
		Creates and run a filechooser dialog to
		select the dir.
		A Checkbox let you set if the import will be
		recursive.
		"""
		for i in filenames:
			if walk:
				self.addDirectories(i)
			else:
				files = [os.path.join(i, k)  for k in os.listdir(i) \
					if os.path.isfile(os.path.join(i, k))]
				if files:
					self.addFiles(files = files)
		return True
		
	
	def addDirectories(self, dir):
		"""
		Recursive import, first and only argument
		is the dir where to digg
		"""
		a         = os.walk(dir)
		f         = []
		filenames = []
		self.f = []
		xml = self.share.getTemplate('walkdirectories')
		dialog = xml['dialog1']
		dialog.show()
		progress = xml['progressbar1']
		label = xml['label1']
		self.__walking = True
		gobject.idle_add(self.__walkDirectories, a, f, filenames, label, dialog)
		gobject.idle_add(self.__walkProgressPulse, progress)
		dialog.connect('response', self.__addDirectories_response)
	
	def __addDirectories_response(self, dialog, response):
		self.__walking = False
		dialog.destroy()

	def __walkProgressPulse(self, progress):
		progress.pulse()
		return self.__walking

	def __walkDirectories(self, a, f, filenames, label, dialog):
		#if not self.__walking:
		#	return False
		try:
			(dirpath, dirnames, files) = a.next()
			filenames.append([dirpath, files])
			npath = self.encode_text(dirpath)
			label.set_text(translate('Exploring') + '%s'%npath)
			allowdexts = self.christineConf.getString('backend/allowed_files')
			allowdexts = allowdexts.split(',')
			for path in filenames[-1][1]:
				ext    = path.split('.').pop().lower()
				exists = os.path.join(filenames[-1][0], path) in self.f
				if ext in allowdexts and not exists:
					f.append(os.path.join(filenames[-1][0],path))
		except StopIteration:
			dialog.destroy()
			self.__walking = False
			if f:
				self.addFiles(files = f)
			return False
		return True

	def __addFile(self, ):
		"""
		Add a single file, to the library or queue.
		the files are taken from the self.__FilesToAdd
		list. the only one argument is queue, wich defines
		if the importing is to the queue
		"""
		gobject.idle_add(self.__addFileCycle, self)
		

	def __addFileCycle(self):
		for i in  xrange(1,2):
			if self.__FilesToAdd:
				new_file = self.__FilesToAdd.pop()
				self.add(new_file)
				self.__updateAddProgressBar(new_file)
			else:
				self.__AddWindow.destroy()
				self.__walking = False
				return False
		return True

	def __updateAddProgressBar(self, file):
		length = len(self.__FilesToAdd)
		self.__Percentage = 1
		if length:
			self.__Percentage = (1 - (length / float(self.__TimeTotalNFiles)))
		if self.__Percentage > 1.0:
			self.__Percentage = 1.0
		# Setting the value and text in the progressbar
		self.__AddProgress.set_fraction(self.__Percentage)
		rest = (self.__TimeTotalNFiles - length)
		text = "%d/%d" % (rest, self.__TimeTotalNFiles)
		self.__AddProgress.set_text(text)
		filename = self.encode_text(os.path.split(file)[1])
		self.__AddFileLabel.set_text(filename)
		return length

	def addFiles(self,files):
		"""
		Add files to the library or to the queue
		"""
		XML = self.share.getTemplate('addFiles')
		XML.signal_autoconnect(self)

		self.__AddWindow       = XML['window']
		self.__AddWindow.set_transient_for(self.interface.coreWindow)
		self.__AddProgress     = XML['progressbar']
		self.__AddCloseButton  = XML['close']
		self.__AddCloseButton.connect('clicked',lambda *args: self.importCancel())
		self.__AddFileLabel    = XML['file_label']
		self.__AddFileLabel.set_text('None')
		self.__AddWindow.connect('destroy', lambda *args: self.importCancel())
		self.__AddWindow.show_all()
		self.__AddWindow.set_modal(True)
		self.__AddWindow.set_modal(False)
		self.__AddWindow.set_property('modal', False)

		#self.__AddCloseButton.grab_add()
		# Be sure that we are working with a list of files
		if not isinstance(files, list):
			raise TypeError, "files must be List, got %s" % type(files)
		files.reverse()
		# Global variable to save temporal files and paths
		self.__Paths      = []
		self.model.basemodel.foreach(self.getPaths)
		extensions = self.christineConf.getString('backend/allowed_files')
		extensions = extensions.split(',')
		iterator = iter(files)
		while True:
			try:
				i = iterator.next()
				ext = i.split('.').pop().lower()
				if not i in self.__Paths and ext in extensions:
					self.__FilesToAdd.append(i)
			except StopIteration:
				break
		self.__Percentage      = 0
		self.__TimeTotalNFiles = len(self.__FilesToAdd)
		gobject.idle_add(self.__addFileCycle)
	
	def importCancel(self):
		"""
		Cancel de import stuff
		"""
		self.__AddCloseButton.grab_remove()
		self.__FilesToAdd = []
		self.__AddWindow.destroy()
		
	def getPaths(self, model, path, iter):
		"""
		Gets path from
		"""
		self.__Paths.append(model.get_value(iter, PATH))
	
		
class library(gtk.Widget,libraryBase):
	__gsignals__= {
				'popping_menu' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								(gobject.TYPE_PYOBJECT,))
				}
	def __init__(self):
		gobject.GObject.__init__(self)
		libraryBase.__init__(self)
		self.interface.mainLibrary = self 
		self.__logger = LoggerManager().getLogger('Library')
		self.tv.connect('button-press-event', self.popupMenuHandlerEvent)
		self.tv.connect('key-press-event',    self.handlerKeyPress)
		self.tv.connect('row-activated',      self.itemActivated)
		self.scroll.show_all()
		self.Events.addWatcher('gotTags', self.gotTags)
		self.interface.Player.connect('set-location', self.change_last_played)
	
	def change_last_played(self, player, last_location, current_location):
		iter = self.model.basemodel.search_iter_on_column(last_location, PATH)
		if (iter != None):
			pix = self.share.getImageFromPix('blank')
			pix = pix.scale_simple(20, 20, gtk.gdk.INTERP_BILINEAR)
			path = self.model.basemodel.get_path(iter)
			self.set(path, PIX, pix)
		iter = self.model.basemodel.search_iter_on_column(current_location, PATH)
		if iter != None:
			count = self.model.getValue(iter, PLAY_COUNT)
			self.model.setValues(iter, PLAY_COUNT, count + 1)
	
	def gotTags(self, tags):
		title = tags['title']
		artist = tags['artist']
		album = tags['album']
		genre = tags['genre']
		track_number  = tags['track_number']
		type_file = self.interface.Player.getType()
		
		search = '.'.join([title,artist, album, genre, type_file])

		self.updateData(self.interface.Player.getLocation(),
								title=title,
								album= album,
								artist=artist,
								track_number=track_number,
								search=search,
								genre=genre)
		gobject.timeout_add(100,self.do_check_file_data)
	
	def do_check_file_data(self):
		self.check_file_data(True)
		return False

	def handlerKeyPress(self, treeview, event):
		"""
		Handle the key-press-event in the
		library.
		Current keys: Enter to activate the row
		and 'q' to send the selected song to the
		queue
		"""

		if (event.keyval == gtk.gdk.keyval_from_name('Delete')):
			self.removeFromLibrary()
		elif (event.keyval == gtk.gdk.keyval_from_name('q')):
			selection     = treeview.get_selection()
			iter = selection.get_selected()[1]
			name          = self.model.getValue(iter, PATH)
			self.interface.Queue.add(name)

	def popupMenuHandlerEvent(self, widget, event):
		"""
		handle the button-press-event in the library
		"""
		if (event.button == 3):
			XML = self.share.getTemplate('PopupMenu')
			XML.signal_autoconnect(self)
			popup = XML['menu']
			popup.popup(None, None, None, 3, gtk.get_current_event_time())
			self.emit('popping_menu', popup)
			self.interface.library_popup = popup
			self.Events.executeEvent('main-library-pupup-menu')
			popup.show_all()
			
	def popupAddToQueue(self, widget):
		"""
		Add the selected item to the queue
		"""
		selection       = self.tv.get_selection()
		(model, iter,)  = selection.get_selected()
		file            = model.get_value(iter, PATH)
		self.interface.Queue.add(file)
	
	def removeFromLibrary(self, widget = None):
		"""
		Remove file from library
		"""
		selection     = self.tv.get_selection()
		(model, iter) = selection.get_selected()
		path     = model.get_value(iter, PATH)
		if self.christineConf.getString("backend/last_played") == path:
			self.christineConf.setValue("backend/last_played","")
		self.remove(iter)

	def add_columns(self):
		render = gtk.CellRendererText()
		render.set_property("ellipsize",pango.ELLIPSIZE_END)
		tv = self.tv
		tvc = gtk.TreeViewColumn

		tn = tvc(translate(""),render,text=TN)
		tn.set_sort_column_id(TN)
		tn.set_min_width(30)
		tn.set_resizable(True)
		tn.set_visible(self.gconf.getBool("ui/show_tn"))
		tn.set_visible(True)
		tv.append_column(tn)

		pix = gtk.CellRendererPixbuf()
		name = tvc(translate("Title"))
		name.set_sort_column_id(NAME)
		name.set_resizable(True)
		name.set_fixed_width(250)
		name.pack_start(pix,False)
		rtext = gtk.CellRendererText()
		rtext.set_property("ellipsize",pango.ELLIPSIZE_END)
		name.pack_start(rtext,True)
		name.add_attribute(pix,"pixbuf",PIX)
		name.add_attribute(rtext,"text",NAME)
		tv.append_column(name)

		artist = tvc(translate("Artist"),render,text=ARTIST)
		artist.set_sort_column_id(ARTIST)
		artist.set_resizable(True)
		artist.set_fixed_width(150)
		artist.set_visible(self.gconf.getBool("ui/show_artist"))
		tv.append_column(artist)

		album = tvc(translate("Album"),render,text=ALBUM)
		album.set_sort_column_id(ALBUM)
		album.set_resizable(True)
		album.set_fixed_width(150)
		album.set_visible(self.gconf.getBool("ui/show_album"))
		tv.append_column(album)

		type = tvc(translate("Type"),render,text=TYPE)
		type.set_sort_column_id(TYPE)
		type.set_resizable(True)
		type.set_min_width(80)
		type.set_visible(self.gconf.getBool("ui/show_type"))
		tv.append_column(type)

		play = tvc(translate("Count"),render,text=PLAY_COUNT)
		play.set_sort_column_id(PLAY_COUNT)
		play.set_resizable(True)
		play.set_visible(self.gconf.getBool("ui/show_play_count"))
		play.set_min_width(50)
		tv.append_column(play)

		length = tvc(translate("Lenght"),render,text=TIME)
		length.set_sort_column_id(TIME)
		length.set_resizable(True)
		length.set_visible(self.gconf.getBool("ui/show_length"))
		length.set_min_width(80)
		tv.append_column(length)

		genre = tvc(translate("Genre"),render,text=GENRE)
		genre.set_sort_column_id(GENRE)
		genre.set_resizable(True)
		genre.set_visible(self.gconf.getBool("ui/show_genre"))
		genre.set_min_width(250)
		tv.append_column(genre)
		
		for i in (tn, name, artist, album, type, play, length, genre):
			i.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)


		self.gconf.notifyAdd("ui/show_artist",self.gconf.toggleVisible,artist)
		self.gconf.notifyAdd("ui/show_album",self.gconf.toggleVisible,album)
		self.gconf.notifyAdd("ui/show_type",self.gconf.toggleVisible,type)
		self.gconf.notifyAdd("ui/show_tn",self.gconf.toggleVisible,tn)
		self.gconf.notifyAdd("ui/show_play_count",self.gconf.toggleVisible,play)
		self.gconf.notifyAdd("ui/show_length",self.gconf.toggleVisible,length)
		self.gconf.notifyAdd("ui/show_genre",self.gconf.toggleVisible,genre)
		self.tv.set_property('fixed-height-mode', True)

	def stream_length(self,widget=None,n=1):
		try:
			total = self.interface.Player.query_duration(gst.FORMAT_TIME)[0]
			ts = total/gst.SECOND
			text = "%02d:%02d"%divmod(ts,60)
			self.model.set(self.iters[self.interface.Player.getLocation()],
					TIME,text)
		except gst.QueryError:
			pass
		return True

class queue (libraryBase ,gobject.GObject):
	__gsignals__= {
				'size-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
								(gobject.TYPE_PYOBJECT,))
				}
	def __init__(self):
		gobject.GObject.__init__(self)
		libraryBase.__init__(self)
		self.__logger = LoggerManager().getLogger('Library')
		self.last_check = -1
		self.loadLibrary('queue')
		self.tv.connect('key-press-event', self.QueueHandlerKey)
		gobject.timeout_add(1000, self.checkQueue)
		self.scroll.set_size_request(100,150)
		self.interface.Queue = self
		self.tv.set_property('fixed-height-mode', False)

	def add_columns(self):
		render = gtk.CellRendererText()
		tv = self.tv
		pix = gtk.CellRendererPixbuf()
		icon = gtk.TreeViewColumn("",pix,pixbuf=PIX)
		icon.set_sort_column_id(TYPE)
		name = gtk.TreeViewColumn(translate("Queue"),render,markup=NAME)
		name.set_sort_column_id(NAME)
		tv.append_column(name)
		#name.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		tv.set_headers_visible(False)

	def add(self,file,prepend=False):
		if isinstance(file, tuple):
			file = file[0]
		if not os.path.isfile(file):
			self.__logger.warning(translate("I can't find the file %s"),file)
			return False
		name = os.path.split(file)[1]
		if isinstance(name,()):
			name = name[0]
		################################
		tags = self.tagger.readTags(file)

		if tags["title"] == "":
			n = os.path.split(file)[1].split(".")
			tags["title"] = ".".join([k for k in n[:-1]])

		if "video-codec" in tags.keys() or \
				os.path.splitext(file)[1][1:] in CHRISTINE_VIDEO_EXT:
			t = "video"
		else:
			t = "audio"

		if type(tags["track"]) !=  type(1):
			tags["track"] = 0

		name	= self.strip_XML_entities(self.encode_text(tags["title"]))
		album	= self.strip_XML_entities(self.encode_text(tags["album"]))
		artist	= self.strip_XML_entities(self.encode_text(tags["artist"]))
		tn		= tags["track"]
		genre	= self.strip_XML_entities(self.encode_text(tags["genre"]))
		
		if file.split(":")[0] == "file" or \
				os.path.isfile(file) or \
				os.path.isfile(file.replace('%2C',',')):
			try:
				tags = self.tagger.readTags(file)
			except:
				self.emit_signal("tags-found!")
				return True
			if name == "":
				n = os.path.split(file)[1].split(".")
				name = ".".join([k for k in n[:-1]])
			name = "<b><i>%s</i></b>"%name
			if album !="":
				name += "\n from <i>%s</i>"%album
			if artist != "":
				name += "\n by <i>%s</i>"%artist
		if prepend:
			func = self.model.prepend
		else:
			func = self.model.append
		iter = func(NAME,name,
				PATH,file,
				PIX,self.blank_pix,
				TYPE,t,
				ALBUM,album,
				ARTIST,artist,
				TN,int(tn),
				SEARCH,",".join([name,album,artist]),
				PLAY_COUNT,0,
				GENRE,genre
				)
		self.library_lib[file] = {"title": tags['title'],
				"type":t,"artist":tags['artist'],
				"album":tags['album'],"track_number":int(tn),
				"playcount":0,
				"time":'0:00',
				"genre":tags['genre']}

	def fillModel(self):
		sounds = self.library_lib.get_all()
		pix = self.share.getImageFromPix('blank')
		pix = pix.scale_simple(20, 20, gtk.gdk.INTERP_BILINEAR)
		keys = sounds.keys()
		keys.sort()
		for path,values in sounds.iteritems():
			for key in values.keys():
				if isinstance(values[key],str):
					values[key] = self.strip_XML_entities(self.encode_text(values[key]))
			name	= self.strip_XML_entities(values["title"])
			album	= self.strip_XML_entities(values["album"])
			artist	= self.strip_XML_entities(values["artist"])
			tn		= values["track_number"]
			genre	= self.strip_XML_entities(values["genre"])
			if name :
				n = os.path.split(path)[1].split(".")
				name = ".".join([k for k in n[:-1]])
			name = "<b><i>%s</i></b>"%name
			if album !="":
				try:
					name += "\n from <i>%s</i>"%album
				except:
					pass
			if artist != "":
				try:
					name += "\n by <i>%s</i>"%artist
				except:
					pass
				
			iter = self.model.append(PATH,path,
					NAME, name,
					SEARCH,
					''.join((values['title'], values['artist'],values['album'],	values['type'])),
					PIX,pix,
					TYPE,values['type'],
					ARTIST,values['artist'],
					ALBUM ,values['album'],
					TN,values['track_number'],
					PLAY_COUNT ,values['playcount'],
					TIME ,values['time'],
					GENRE ,values['genre'])
			self.iters[path] = iter

	def QueueHandlerKey(self, widget, event): 
		"""
		Handler the key-press-event in the queue list
		"""
		if (event.keyval == gtk.gdk.keyval_from_name('Delete')):
			selection     = self.tv.get_selection()
			(model, iter) = selection.get_selected()

			if (iter is not None):
				name = model.get_value(iter, NAME)
				self.remove(iter)
				
	def	checkQueue(self):
		model = self.tv.get_model()
		size = len(model) 
		if size != self.last_check:
			self.emit('size-changed', size)
			self.last_check = size
		return True
	
	def itemActivated(self, widget, path, iter):
		libraryBase.itemActivated(self, widget, path, iter)
		self.remove(iter)
