scriptsdir = @PYTHON_LIB_DIR@/lib_christine

scripts_DATA=__init__.py \
gtk_misc.py \
library.py \
libs_christine.py \
preferences.py \
about.py \
Discoverer.py \
Player.py \
gst_base.py \
display.py \
sources_list.py \
Translator.py \
plugins.py \
Christine.py \
queue.py \
clibrary.so

DISTFILES= Makefile.in \
		   gtk_misc.py.in \
		   about.py.in \
		   Translator.py.in \
		   libs_christine.py.in \
		   clibrary.c \
		   plugins.py.in \
		   Christine.py.in \
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

Translator.py: Makefile $(srcdir)/Translator.py.in
	$(edit) $(srcdir)/Translator.py.in > Translator.py

plugins.py: Makefile $(srcdir)/plugins.py.in
	$(edit) $(srcdir)/plugins.py.in > plugins.py

libs_christine.py: Makefile $(srcdir)/libs_christine.py.in
	$(edit) $(srcdir)/libs_christine.py.in > libs_christine.py

clibrary.so: Makefile $(srcdir)/clibrary.c
	gcc -Wall ${CFLAGS} -I${pythonincludedir} -I${usr_libdir} -c -o clibrary.o clibrary.c
	gcc -shared clibrary.o -o clibrary.so -L${pythonincludedir}

Christine.py: Makefile $(srcdir)/Christine.py.in
	    $(edit) $(srcdir)/Christine.py.in > Christine.py

all: all-am

all-am: 

clean:
	rm Christine.py
	rm gtk_misc.py
	rm about.py
	rm clibrary.o
	rm clibrary.so
	rm Translator.py
	rm plugins.py
	rm libs_christine.py
