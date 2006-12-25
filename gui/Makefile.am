SUBDIRS=pixmaps
scriptsdir = @datadir@/christine/gui

scripts_DATA=__init__.py \
about.glade \
add_files.glade \
delete_file_from_disk_dialog.glade \
dir_selector.glade \
error.glade \
file_selector.glade \
icon_view.glade \
jump_to.glade \
main_window.glade \
miniviewer.glade \
open_remote.glade \
popmenu.glade \
preferences.glade \
properties.glade \
sources_treeview.glade \
tray_menu.glade \
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
