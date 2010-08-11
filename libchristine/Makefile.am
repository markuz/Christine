scriptsdir = @PYTHON_LIB_DIR@/libchristine


DISTFILES= Makefile.in \
		   globalvars.py.in \
		   cglobalvars.c \
		   CLibraryModel.c \
		   CLibraryModel.h\
			christineConf.py \
			christineLogger.py \
			Christine.py \
			Events.py \
			__init__.py \
			LibraryModel.py \
			Library.py \
			libs_christine.py \
			Logger.py \
			options.py \
			Player.py \
			Share.py \
			sources_list.py \
			Tagger.py \
			Translator.py \
			ui.py \
			Validator.py \
			ChristineCore.py \
			globalvars.py \
			sanity.py \
			envelopes.py

scripts_DATA=${DISTFILES} \
			 CLibraryModel.so
			 cglobalvars.so

pkgdatadir=${datadir}
pkgsysconfdir=${sysconfdir}
pythonincludedir = @PYTHON_INCLUDE_DIR@
pythonlibdir = @PYTHON_LIB_DIR@
pythonlfs = @PYTHON_LFS@
usr_libdir = @includedir@
pythonversion = @PYTHON_VERSION@

programname=@PROGRAM_NAME@
version=@VERSION@

edit = sed \
	   -e 's,@datadir\@,$(pkgdatadir),g' \
	   -e 's,@prefix\@,$(prefix),g' \
	   -e 's,@sysconfdir\@,$(pkgsysconfdir),g' \
	   -e 's,@programname\@,$(programname),g' \
	   -e 's,@pythonlibdir\@,$(pythonlibdir),g' \
	   -e 's,@version\@,$(version),g'

globalvars.py: Makefile $(srcdir)/globalvars.py.in
	$(edit) $(srcdir)/globalvars.py.in > globalvars.py


CLibraryModel.so:  Makefile $(srcdir)/CLibraryModel.so
	$(CC) ${CFLAGS} -Wall -fPIC ${CFLAGS} -I${pythonincludedir}/ -I/usr/include/ -c CLibraryModel.c -o CLibraryModel.o
	$(CC) -shared ${CFLAGS} ${LDFLAGS} ${pythonlfs} CLibraryModel.o -L/usr/lib -L/usr/local/lib -lnsl -ldl -lieee -lpthread -lutil -lm -lpython${pythonversion}  -o CLibraryModel.so

cglobalvars.so:  Makefile $(srcdir)/cglobalvars.so
	$(CC) ${CFLAGS} -Wall -fPIC ${CFLAGS} -I${pythonincludedir}/ -I/usr/include/ -c cglobalvars.c -o cglobalvars.o
	$(CC) -shared ${CFLAGS} ${LDFLAGS} ${pythonlfs} cglobalvars.o -L/usr/lib -L/usr/local/lib -lnsl -ldl -lieee -lpthread -lutil -lm -lpython${pythonversion}  -o cglobalvars.so

all: cglobalvars.so

clean:
	rm $(srcdir)/*.pyc &
	rm globalvars.py &
	rm CLibraryModel.o &
	rm CLibraryModel.so &
	rm cglobalvars.o &
	rm cglobalvars.so &
