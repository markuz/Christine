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
Plugins.py \
Christine.py \
Share.py \
Queue.py \
Validator.py \
ChristineGConf.py \
Tagger.py \
LibraryModel.py \
BugReport.py 


DISTFILES= Makefile.in \
		   GtkMisc.py.in \
		   About.py.in \
		   Translator.py.in \
		   libs_christine.py.in \
		   clibrary.c \
		   Plugins.py.in \
		   Christine.py.in \
		   Share.py.in \
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

GtkMisc.py: Makefile $(srcdir)/GtkMisc.py.in
	$(edit) $(srcdir)/GtkMisc.py.in > GtkMisc.py

About.py: Makefile $(srcdir)/About.py.in
	$(edit) $(srcdir)/About.py.in > About.py

Translator.py: Makefile $(srcdir)/Translator.py.in
	$(edit) $(srcdir)/Translator.py.in > Translator.py

Plugins.py: Makefile $(srcdir)/Plugins.py.in
	$(edit) $(srcdir)/Plugins.py.in > Plugins.py

libs_christine.py: Makefile $(srcdir)/libs_christine.py.in
	$(edit) $(srcdir)/libs_christine.py.in > libs_christine.py

Christine.py: Makefile $(srcdir)/Christine.py.in
	    $(edit) $(srcdir)/Christine.py.in > Christine.py

Share.py: Makefile $(srcdir)/Share.py.in
		$(edit) $(srcdir)/Share.py.in > Share.py

all: all-am

all-am: 

clean:
	rm $(srcdir)/Share.py
	rm $(srcdir)/Christine.py
	rm $(srcdir)/GtkMisc.py
	rm $(srcdir)/About.py
	rm $(srcdir)/clibrary.o
	rm $(srcdir)/clibrary.so
	rm $(srcdir)/Translator.py
	rm $(srcdir)/Plugins.py
	rm $(srcdir)/libs_christine.py
