scriptsdir = @pythondir@/lib_christine

scripts_DATA=__init__.py \
gtk_misc.py \
library.py \
libs_christine.py \
preferences.py \
show_properties.py 

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

gtk_misc.py: Makefile $(srcdir)/gtk_misc.py.in
	$(edit) $(srcdir)/gtk_misc.py.in > gtk_misc.py

all: all-am

all-am: 

clean:
	rm gtk_misc.py
