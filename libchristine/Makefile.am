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
Tagger.py \
Logger.py \
Dispatcher.py \
ChristineDefinitions.py \
clibrary.so

DISTFILES= Makefile.in \
		   About.py.in \
		   Translator.py.in \
		   libs_christine.py.in \
		   clibrary.c \
		   Plugins.py.in \
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

About.py: Makefile $(srcdir)/About.py.in
	$(edit) $(srcdir)/About.py.in > About.py

Translator.py: Makefile $(srcdir)/Translator.py.in
	$(edit) $(srcdir)/Translator.py.in > Translator.py

clibrary.so: Makefile $(srcdir)/clibrary.c
	gcc -Wall -fPIC ${CFLAGS} -I${pythonincludedir} -I${usr_libdir} -c -o clibrary.o clibrary.c
	gcc -shared clibrary.o -o clibrary.so -L${pythonincludedir}

ChristineDefinitions.py: Makefile $(srcdir)/ChristineDefinitions.py.in
	    $(edit) $(srcdir)/ChristineDefinitions.py.in > ChristineDefinitions.py

all: all-am

all-am: 

clean:
	rm $(srcdir)/ChristineDefinitions.py
	rm $(srcdir)/About.py
	rm $(srcdir)/clibrary.o
	rm $(srcdir)/clibrary.so
	rm $(srcdir)/Translator.py
