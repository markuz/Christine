SUBDIRS=pixmaps
scriptsdir = @datadir@/christine/gui

scripts_DATA= About.glade \
addFiles.glade \
deleteFileFromDisk.glade \
deleteQuestion.glade \
directorySelector.glade \
Error.glade \
errorReporter.glade \
FileSelector.glade \
genericQuestion.glade \
iconView.glade \
JumpTo.glade \
mainWindow.glade \
MenuTrayIcon.glade \
miniViewer.glade \
NewSourceDialog.glade \
openRemote.glade \
plugin_lastfm_main.glade \
plugin_pidgin_main.glade \
PopupMenu.glade \
Preferences.glade \
Properties.glade \
SourcesList.glade \
TreeViewReorderable.glade \
TreeViewSources.glade \
walkdirectories.glade \
WindowCore.glade

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
