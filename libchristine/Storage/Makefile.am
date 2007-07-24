scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=__init__.py \
ChristineGConf.py 

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
