SUBDIRS = libchristine \
		  gui \
		  po \
		  libchristine/pattern/ \
		  libchristine/gui/ \
		  libchristine/Storage/ \
		  libchristine/Plugins/

bin_SCRIPTS = christine


DIST_FILES = config.rpath \
	   	    mkinstalldirs \
	   	   	christine.desktop.in \
	   	   	christine.c 
	   	   	
EXTRA_DIST = config.rpath  config.rpath  createDeb.sh.in \
			 $(DIST_FILES)

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
	rm -rf createDeb.sh

all: all-am
	chmod 755 christine

christine.desktop: Makefile $(srcdir)/christine.desktop.in
	$(edit) $(srcdir)/christine.desktop.in > christine.desktop

createDeb.sh: Makefile $(srcdir)/createDeb.sh.in
	$(edit) $(srcdir)/createDeb.sh.in > createDeb.sh

run:
	./christine --devel $*

christine: Makefile $(srcdir)/christine.c
	gcc -Wall -fPIC ${CFLAGS} -I${pythonincludedir} -c christine.c -o christine.o
	gcc -Xlinker -export-dynamic christine.o ${pythonlibdir}/libpython${pythonversion}.a -lnsl -ldl -lieee -lpthread -lutil -lm -o christine
	python -c "import compileall,re; compileall.compile_dir('./', rx=re.compile('/[.]svn'),force=True, maxlevels=11)"



ACLOCAL_AMFLAGS = -I m4
