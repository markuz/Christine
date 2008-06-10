SUBDIRS=pixmaps
scriptsdir = @datadir@/christine/gui

scripts_DATA= About.glade \
Error.glade \
FileSelector.glade \
JumpTo.glade \
MenuTrayIcon.glade \
PopupMenu.glade \
Preferences.glade \
Properties.glade \
TreeViewReorderable.glade \
TreeViewSources.glade \
WindowCore.glade \
addFiles.glade \
deleteFileFromDisk.glade \
directorySelector.glade \
iconView.glade \
miniViewer.glade \
openRemote.glade \
deleteQuestion.glade \
genericQuestion.glade \
SourcesList.glade \
NewSourceDialog.glade \
errorReporter.glade \
walkdirectories.glade


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
