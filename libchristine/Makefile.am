scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=__init__.py \
GtkMisc.py \
Library.py \
libs_christine.py \
Preferences.py \
About.py \
Discoverer.py \
Player.py \
GstBase.py \
Display.py \
sources_list.py \
Translator.py \
Christine.py \
Share.py \
Queue.py \
Validator.py \
christineConf.py \
Tagger.py \
LibraryModel.py \
BugReport.py \
globalvars.py


DISTFILES= Makefile.in \
		   $(scripts_DATA) 


pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}
pythonincludedir = @PYTHON_INCLUDE_DIR@
usr_libdir = @includedir@

programname=@PROGRAM_NAME@
version=@VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(programname),g' \
	   -e 's,@version\@,$(version),g'

globalvars.py: Makefile $(srcdir)/globalvars.py.in
	$(edit) $(srcdir)/globalvars.py.in > globalvars.py

all: all-am

all-am: 

clean:
	rm $(srcdir)/Share.py
	rm $(srcdir)/Christine.py
	rm $(srcdir)/GtkMisc.py
	rm $(srcdir)/About.py
	rm $(srcdir)/Translator.py
	rm $(srcdir)/Plugins.py
	rm $(srcdir)/libs_christine.py
