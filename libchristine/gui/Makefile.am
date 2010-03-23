scriptsdir = @PYTHON_LIB_DIR@/libchristine/gui/

scripts_DATA=__init__.py \
			About.py \
			BugReport.py \
			Display.py \
			Preferences.py \
			GtkMisc.py \
			openRemote.py \
			buttons.py \
			mainWindow.py \
			Volume.so 

DISTFILES=Makefile.in \
		  Volume.c \
			${scripts_DATA}


pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}
pythonincludedir = @PYTHON_INCLUDE_DIR@
usr_libdir = @includedir@
pythonversion = @PYTHON_VERSION@

programname=@PROGRAM_NAME@
version=@VERSION@
GTK_FLAGS=$(shell pkg-config --cflags --libs gtk+-2.0)
GTK_LINK=$(shell pkg-config --libs gtk+-2.0)
PYGTK_FLAGS=$(shell pkg-config --cflags --libs pygtk-2.0)
PYGTK_LINK=$(shell pkg-config --libs pygtk-2.0)

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(programname),g' \
	   -e 's,@version\@,$(version),g'

Volume.so:  Makefile $(srcdir)/Volume.so
	$(CC) ${CFLAGS} -Wall -fPIC ${CFLAGS} -I${pythonincludedir}/ $(GTK_FLAGS) $(PYGTK_FLAGS)  -I/usr/include/ -c Volume.c -o Volume.o
	$(CC) -shared ${CFLAGS} ${LDFLAGS} ${pythonlfs} $(GTK_FLAGS) $(PYGTK_FLAGS)  Volume.o -L/usr/lib -L/usr/local/lib -lnsl -ldl -lieee -lpthread -lutil -lm -lpython${pythonversion}  -o Volume.so


clean:
	rm -v $(srcdir)/*.pyc &
	rm -v $(srcdir)/Volume.o&
	rm -v $(srcdir)/Volume.so&
