scriptsdir = @datadir@/christine/gui/pixmaps

scripts_DATA= blank.png \
logo.png \
sort.png \
sound.png \
usort.png \
video.png 

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

all: all-am

all-am: 
