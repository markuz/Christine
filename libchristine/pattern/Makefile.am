scriptsdir = @PYTHON_LIB_DIR@/libchristine/pattern

scripts_DATA=__init__.py \
			 Singleton.py
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

all: all-am

all-am: 

clean:
	rm Share.py
	rm Christine.py
	rm GtkMisc.py
	rm About.py
	rm clibrary.o
	rm clibrary.so
	rm Translator.py
	rm plugins.py
	rm libs_christine.py
