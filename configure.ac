AC_INIT('christine', '0.0.4-svn', markuz@gnu.org.mx)
AM_INIT_AUTOMAKE('christine', '0.0.4-svn')

AC_CONFIG_SRCDIR(libchristine)
AC_CONFIG_SRCDIR(gui)

AM_MAINTAINER_MODE

AC_PATH_X
AC_HEADER_STDC
AC_PROG_CC
AC_HEADER_STDC

AM_MAINTAINER_MODE
AM_PATH_PYTHON
AM_PROG_LIBTOOL
LIBTOOL="$LIBTOOL --silent"
AC_PROG_CC
AC_PROG_INSTALL
PKG_PROG_PKG_CONFIG

PKG_CHECK_MODULES(pygtk, pygtk-2.0)
PKG_CHECK_MODULES(gstreamer,gstreamer-0.10)
PKG_CHECK_MODULES(gst_python,gst-python-0.10)
PKG_CHECK_MODULES(gnome_python,gnome-python-2.0)
PKG_CHECK_MODULES(gnome_python_extras,gnome-python-extras-2.0)
PKG_CHECK_MODULES(gconf,gconf-2.0)
PKG_CHECK_MODULES(glib,glib-2.0)

AC_SUBST(pygtk_CFLAGS)
AC_SUBST(pygtk_LIBS)

PROGRAM_NAME="christine"
VERSION="0.0.4-svn"
PREFIX=/usr
PYTHON_INCLUDE_DIR=`python -c "from distutils import sysconfig; print sysconfig.get_python_inc()"`
PYTHON_LIB_DIR=`python -c "from distutils import sysconfig; print sysconfig.get_python_lib()"`

# gross readline autconf kludge courtesy of samba -- thanks tpot!
# Samba original version is in 1.10; I've improved it a bit to work with
# libreadline-4.1
###############################################
# Readline included by default unless explicitly asked not to
test "${with_readline+set}" != "set" && with_readline=yes

# test for where we get readline() from
AC_MSG_CHECKING(whether to use readline)
AC_ARG_WITH(readline,
[  --with-readline[=DIR]   Look for readline include/libs in DIR
  --without-readline      Don't include readline support],
[  case "$with_readline" in
  yes)
    AC_MSG_RESULT(yes)

    AC_CHECK_HEADERS(readline.h history.h readline/readline.h)
    AC_CHECK_HEADERS(readline/history.h)

    AC_CHECK_HEADERS(readline.h readline/readline.h,[
      for termlib in ncurses curses termcap terminfo termlib; do
       AC_CHECK_LIB(${termlib}, tgetent, [TERMLIBS="-l${termlib}"; break])
      done
      AC_CHECK_LIB(readline, rl_callback_handler_install,
       [TERMLIBS="-lreadline $TERMLIBS"
       AC_DEFINE(HAVE_LIBREADLINE, 1, [Do we have libreadline?])
       break], [TERMLIBS=], $TERMLIBS)])

      AC_CHECK_LIB(readline, rl_completion_matches,
	   [AC_DEFINE(HAVE_LIBREADLINE_NEW, 1, 
	      [Do we have rl_completion_matches?])])
    ;;
  no)
    AC_MSG_RESULT(no)
    ;;
  *)
    AC_MSG_RESULT(yes)

    # Needed for AC_CHECK_HEADERS and AC_CHECK_LIB to look at
    # alternate readline path
    _ldflags=${LDFLAGS}
    _cppflags=${CPPFLAGS}

    # Add additional search path
    LDFLAGS="-L$with_readline/lib $LDFLAGS"
    CPPFLAGS="-I$with_readline/include $CPPFLAGS"

    AC_CHECK_HEADERS(readline.h history.h readline/readline.h)
    AC_CHECK_HEADERS(readline/history.h)

    AC_CHECK_HEADERS(readline.h readline/readline.h,[
      for termlib in ncurses curses termcap terminfo termlib; do
       AC_CHECK_LIB(${termlib}, tgetent, [TERMLIBS="-l${termlib}"; break])
      done
      AC_CHECK_LIB(readline, rl_callback_handler_install,
       [TERMLDFLAGS="-L$with_readline/lib"
       TERMCPPFLAGS="-I$with_readline/include"
       CPPFLAGS="-I$with_readline/include $CPPFLAGS"
       TERMLIBS="-lreadline $TERMLIBS"
       AC_DEFINE(HAVE_LIBREADLINE, 1, [Do we have libreadline?])
       break], [TERMLIBS= CPPFLAGS=$_cppflags], $TERMLIBS)])


      AC_CHECK_LIB(readline, rl_completion_matches,
	   [AC_DEFINE(HAVE_LIBREADLINE_NEW, 1, 
	      [Do we have rl_completion_matches?])])
    LDFLAGS=$_ldflags
    ;;
  esac],
  AC_MSG_RESULT(no)
)
AC_SUBST(TERMLIBS)
AC_SUBST(TERMLDFLAGS)


AC_SUBST(PROGRAM_NAME)
AC_SUBST(VERSION)
AC_SUBST(PREFIX)
AC_SUBST(PYTHON_INCLUDE_DIR)
AC_SUBST(PYTHON_LIB_DIR)

GETTEXT_PACKAGE=christine
AC_SUBST(GETTEXT_PACKAGE)
ALL_LINGUAS="es_ES"
AC_SUBST(ALL_LINGUAS)
USE_NLS=yes
AC_SUBST(USE_NLS)
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL

AC_CONFIG_FILES([
Makefile
libchristine/Makefile
cplugins/Makefile
gui/Makefile
gui/pixmaps/Makefile
po/Makefile.in
po/Makefile
po/POTFILES
intltool-extract
intltool-merge
intltool-update
])

AC_OUTPUT

echo 
echo $PROGRAM_NAME will be installed in......: ${prefix}/bin

