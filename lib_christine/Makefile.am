scriptsdir = @PYTHON_LIB_DIR@/lib_christine

scripts_DATA=__init__.py \
gtk_misc.py \
library.py \
libs_christine.py \
preferences.py \
about.py \
discoverer.py \
player.py \
gst_base.py \
display.py \
sources_list.py \
trans.py \
plugins.py \
christine.py \
queue.py \
clibrary.so

DISTFILES= Makefile.in \
		   gtk_misc.py.in \
		   about.py.in \
		   trans.py.in \
		   libs_christine.py.in \
		   clibrary.c \
		   plugins.py.in \
		   christine.py.in \
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

gtk_misc.py: Makefile $(srcdir)/gtk_misc.py.in
	$(edit) $(srcdir)/gtk_misc.py.in > gtk_misc.py

about.py: Makefile $(srcdir)/about.py.in
	$(edit) $(srcdir)/about.py.in > about.py

trans.py: Makefile $(srcdir)/trans.py.in
	$(edit) $(srcdir)/trans.py.in > trans.py

plugins.py: Makefile $(srcdir)/plugins.py.in
	$(edit) $(srcdir)/plugins.py.in > plugins.py

libs_christine.py: Makefile $(srcdir)/libs_christine.py.in
	$(edit) $(srcdir)/libs_christine.py.in > libs_christine.py

clibrary.so: Makefile $(srcdir)/clibrary.c
	gcc -Wall ${CFLAGS} -I${pythonincludedir} -I${usr_libdir} -c -o clibrary.o clibrary.c
	gcc -shared clibrary.o -o clibrary.so -L${pythonincludedir}

christine.py: Makefile $(srcdir)/christine.py.in
	    $(edit) $(srcdir)/christine.py.in > christine.py

all: all-am

all-am: 

clean:
	rm gtk_misc.py
	rm about.py
	rm clibrary.o
	rm clibrary.so
	rm trans.py
	rm plugins.py
	rm libs_christine.py
