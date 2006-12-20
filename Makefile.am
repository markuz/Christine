SUBDIRS = lib_christine gui po

bin_SCRIPTS = christine

EXTRA_DIST = config.rpath mkinstalldirs m4/ChangeLog  mkinstalldirs m4/ChangeLog christine.desktop.in

program_name = @program_name@
PROGRAM_NAME = @PROGRAM_NAME@
desktopdir =  $(datadir)/applications
pkgdatadir = $(datadir)
desktop_DATA = christine.desktop

prefix = @prefix@
sysconfdir = @sysconfdir@

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
christine: Makefile $(srcdir)/christine.in
	$(edit) $(srcdir)/christine.in > christine

ACLOCAL_AMFLAGS = -I m4
