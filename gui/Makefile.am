SUBDIRS=pixmaps
scriptsdir = @datadir@/christine/gui

scripts_DATA=__init__.py \
   	about.glade \
	add_files.glade \
	dir_selector.glade \
	error.glade \
	file_selector.glade \
	icon_view.glade \
	jump_to.glade \
	main_window.glade \
	miniviewer.glade \
	popmenu.glade \
	preferences.glade \
	properties.glade \
	treeview.glade \
	treeview_reorderable.glade

DISTFILES= Makefile.in $(scripts_DATA)

pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}

programname=@PROGRAM_NAME@
version=@VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(programname),g' \
	   -e 's,@version\@,$(version),g'

all: all-am

all-am: 
