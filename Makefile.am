SUBDIRS = libchristine gui po cplugins libchristine/pattern/

bin_SCRIPTS = christine

EXTRA_DIST = config.rpath  config.rpath  config.rpath  config.rpath  config.rpath  config.rpath mkinstalldirs m4/ChangeLog  mkinstalldirs m4/ChangeLog christine.desktop.in christine.c
DIST_FILES = ${EXTRA_DIST}

program_name = @program_name@
PROGRAM_NAME = @PROGRAM_NAME@
desktopdir =  $(datadir)/applications
pkgdatadir = $(datadir)
desktop_DATA = christine.desktop

prefix = @prefix@
sysconfdir = @sysconfdir@
pythonincludedir = @PYTHON_INCLUDE_DIR@
pythonlibdir = @PYTHON_LIB_DIR@/../config
usr_libdir = @includedir@
pythonversion = @PYTHON_VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(PROGRAM_NAME),g' \
	   -e 's,@VERSION\@,$(VERSION),g'

clean-local:
	rm -rf christine.desktop
	rm -rf christine
all: all-am
	chmod 755 christine

christine.desktop: Makefile $(srcdir)/christine.desktop.in
	$(edit) $(srcdir)/christine.desktop.in > christine.desktop

christine: Makefile $(srcdir)/christine.c
	gcc -Wall -fPIC ${CFLAGS} -I${pythonincludedir} -c christine.c -o christine.o
	gcc -Xlinker -export-dynamic christine.o ${pythonlibdir}/libpython${pythonversion}.a -lnsl -ldl -lieee -lpthread -lutil -lm -o christine

ACLOCAL_AMFLAGS = -I m4
