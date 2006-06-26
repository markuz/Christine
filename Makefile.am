SUBDIRS = lib_christine gui

bin_SCRIPTS = christine

EXTRA_DIST = mkinstalldirs m4/ChangeLog christine.desktop.in

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
	   -e 's,@VERSION\@,$(VERSION),g'

clean-local:
	rm -rf christine.desktop
all: all-am
	chmod 755 gpkg

gpkg.desktop: Makefile $(srcdir)/gpkg.desktop.in
	$(edit) $(srcdir)/christine.desktop.in > christine.desktop

ACLOCAL_AMFLAGS = -I m4
