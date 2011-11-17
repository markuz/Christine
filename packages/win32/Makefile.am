DIST_FILES = christine.ico \
			 setup.py \
			 christine.nsi 

EXTRA_DIST = Makefile.in \
			 ${DIST_FILES}

program_name = @PROGRAM_NAME@
PROGRAM_NAME = @PROGRAM_NAME@
desktopdir =  $(datadir)/applications
pkgdatadir = $(datadir)

prefix = @prefix@
sysconfdir = @sysconfdir@
pythonincludedir = @PYTHON_INCLUDE_DIR@
pythonlibdir = @PYTHON_LIB_DIR@/../config
pythonlfs = @PYTHON_LFS@
usr_libdir = @includedir@
pythonversion = @PYTHON_VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(PROGRAM_NAME),g' \
	   -e 's,@VERSION\@,$(VERSION),g'

all: all-am

