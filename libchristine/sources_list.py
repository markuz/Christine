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


from libchristine.gui.GtkMisc import GtkMisc
from libchristine.Share import Share
from libchristine.Translator import  translate
from libchristine.Storage.sqlitedb import sqlite3db
from libchristine.Logger import LoggerManager
from libchristine.gui.keyvals import ENTER, INTRO
import gobject
import gtk

(LIST_NAME,
LIST_TYPE,
LIST_PIXBUF,
LIST_EXTRA) = xrange(4)

class sources_list (GtkMisc):
    def __init__(self):
        GtkMisc.__init__(self)
        self.music_iter = None
        self.__logger = LoggerManager().getLogger('sources_list')
        self.__db = sqlite3db()
        idlist = self.__db.PlaylistIDFromName(list)
        if idlist != None:
            idlist = idlist['id']
        self.__Share = Share()
        xml = self.__Share.getTemplate('SourcesList', 'vbox')
        self.__gen_model()
        self.treeview = xml["treeview"]
        #self.treeview.set_headers_visible(True)
        self.treeview.set_model(self.model)
        self.treeview.expand_all()
        self.treeview.connect('button-press-event', self.treeview_bpe)
        self.vbox = xml['vbox']
        self.vbox.set_size_request(75, 75)
        self.__append_columns()
        
    def treeview_bpe(self, treeview, event):
        if event.button == 3:
            self.__Share = Share()
            #import pdb
            #pdb.set_trace()
            xml = self.__Share.getTemplate('SourcesList', 'menu')
            menu = xml['menu']
            addButton = xml['addSource']
            delButton = xml['delSource']
            addButton.connect('activate', self.addSource)
            delButton.connect('activate', self.delSource)
            menu.popup(None, None, None, 3, event.time)

    def __gen_model(self):
        if not getattr(self, 'model', False):
            self.model = gtk.TreeStore(str, str, gtk.gdk.Pixbuf,gobject.TYPE_PYOBJECT)
        else:
            self.model.clear()
        sources = self.__db.getPlaylists()
        iter = self.model.append(None)
        ltype = 'source'
        self.model.set(iter, LIST_NAME, 'Library', LIST_TYPE, ltype)
        self.music_iter = iter
        for source in sources:
            iter = self.model.append(self.music_iter)
            self.model.set(iter, LIST_NAME, source['name'], LIST_TYPE, ltype)
        
        #Add the albums node:
        ltype = 'radio'
        self.radioiter = self.model.append(None)
        self.model.set(self.radioiter, LIST_NAME, "Radio", LIST_TYPE, ltype)
        radios = self.__db.getRadio()
        for radio in radios:
            iter = self.model.append(self.radioiter)
            self.model.set(iter, LIST_NAME, radio['title'], LIST_TYPE, ltype,
                           LIST_EXTRA, radio)
        if getattr(self, 'treeview', False):
            self.treeview.expand_all()

    def __append_columns(self):
        column = gtk.TreeViewColumn("Source")
        text = gtk.CellRendererText()
        pix = gtk.CellRendererPixbuf()
        column.pack_start(pix, False)
        column.pack_start(text, True)
        column.add_attribute(text, "text", LIST_NAME)
        column.add_attribute(pix, "pixbuf", LIST_PIXBUF)
        self.treeview.append_column(column)

    def addSource(self, button):
        model, iter = self.treeview.get_selection().get_selected()
        type = 'source'
        if iter:
            name, type = model.get(iter,LIST_NAME,LIST_TYPE)
        if type == 'source':
            self.add_source()
        elif type == 'radio':
            self.add_radio()
                    
    def add_source(self):
        xml = self.__Share.getTemplate('NewSourceDialog')
        dialog = xml['dialog']
        entry = xml['entry']
        save = xml['savebtn']
        entry.connect('key-release-event', self.__add_source_entrykre, save)
        response = dialog.run()
        if response == 1:
            exists = False
            for row in self.model:
                name = row[LIST_NAME]
                if entry.get_text() == name:
                    exists = True
                    break
            if not exists:
                self.__db.addPlaylist(entry.get_text())
        self.__gen_model()
        dialog.destroy()
    
    def __add_source_entrykre(self, widget, event,save):
        keyval = event.keyval
        if keyval in (ENTER,INTRO):
            save.clicked()
    
    def add_radio(self):
        xml = self.__Share.getTemplate('NewRadioDialog')
        dialog = xml['dialog']
        entry = xml['entry']
        title_entry = xml['title_entry']
        response = dialog.run()
        dialog.destroy()
        if response == 1:
            title = title_entry.get_text()
            if not title:
                return True
            url = entry.get_text()
            if not url[-3:].lower() == 'pls':
                return True
            exists = self.__db.get_radio_by_url(url)
            if exists:
                return True
            self.__db.add_radio(title, url)
            radio = self.__db.get_radio_by_url(url)
            if radio:
                radio = radio[0]
                iter = self.model.append(self.radioiter)
                self.model.set(iter, LIST_NAME, radio['title'], LIST_TYPE, 'radio',
                       LIST_EXTRA, radio)
            

    def delSource(self, button):
        xml = self.__Share.getTemplate('genericQuestion')
        dialog = xml['dialog']
        label = xml['label']
        label.set_text(translate('Are you sure\nThis cannot be undone'))
        response = dialog.run()
        if response == 1:
            selection = self.treeview.get_selection()
            model, iter = selection.get_selected()
            if iter != None:
                fname, ftype = model.get(iter, LIST_NAME, LIST_TYPE)
                if ftype == 'source':
                    self.__db.removePlayList(fname)
                elif ftype == 'radio':
                    self.__db.removeRadio(fname)
            self.__gen_model()
        dialog.destroy()








