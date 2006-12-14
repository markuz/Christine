scriptsdir = @pythondir@/lib_christine

scripts_DATA=__init__.py \
gtk_misc.py \
library.py \
libs_christine.py \
preferences.py \
show_properties.py \
about.py \
discoverer.py \
player.py \
gst_base.py \
display.py \
sources_list.py \
clibrary.so

DISTFILES= Makefile.in $(scripts_DATA)

pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}
pythonlibdir = @prefix@/include/python@PYTHON_VERSION@/
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

clibrary.so: Makefile $(srcdir)/clibrary.c
	gcc -pedantic -WAll ${CFLAGS} -I${pythonlibdir} -I${usr_libdir} -c -o clibrary.o clibrary.c && gcc -shared clibrary.o -o clibrary.so -L${pythonlibdir}

all: all-am

all-am: 

clean:
	rm gtk_misc.py
	rm about.py
	rm clibrary.so
