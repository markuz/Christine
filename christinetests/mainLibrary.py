#!/usr/bin/env python



from libchristine.Library import library
import gtk



window = gtk.Window()
window.connect('destroy',gtk.main_quit)
window.set_size_request(640,480)
window.set_position(gtk.WIN_POS_CENTER)
Library  = library()
lastSourceUsed = 'music'
Library.loadLibrary(lastSourceUsed)
TreeView = Library.tv
scroll = gtk.ScrolledWindow()
scroll.add(TreeView)
window.add(scroll)
window.show_all()

gtk.main()