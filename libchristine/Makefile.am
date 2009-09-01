scriptsdir = @PYTHON_LIB_DIR@/libchristine

scripts_DATA=christineConf.py \
			christineLogger.py \
			Christine.py \
			Events.py \
			globalvars.py \
			__init__.py \
			LibraryModel.py \
			Library.py \
			libs_christine.py \
			Logger.py \
			options.py \
			Player.py \
			Sanity.py \
			Share.py \
			sources_list.py \
			Tagger.py \
			Translator.py \
			ui.py \
			Validator.py \
			CLibraryModel.so \
			sanity.py

DISTFILES= Makefile.in \
		   globalvars.py.in \
		   CLibraryModel.c \
			${scripts_DATA}


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

all: globalvars.py

clean:
	rm $(srcdir)/*.pyc &
	rm globalvars.py &
	rm CLibraryModel.o &
	rm CLibraryModel.so &
