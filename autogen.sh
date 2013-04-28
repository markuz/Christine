#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
PKG_NAME="christine"

DIE=0

(autoconf --version) < /dev/null > /dev/null 2>&1 || {
  echo
  echo "**Error**: You must have \`autoconf' installed to."
  echo "Download the appropriate package for your distribution,"
  echo "or get the source tarball at ftp://ftp.gnu.org/pub/gnu/"
  DIE=1
}

####(grep "^AM_PROG_LIBTOOL" $srcdir/configure.ac >/dev/null) && {
####  (libtool --version) < /dev/null > /dev/null 2>&1 || {
####    echo
####    echo "**Error**: You must have \`libtool' installed."
####    echo "Get ftp://ftp.gnu.org/pub/gnu/libtool-1.2d.tar.gz"
####    echo "(or a newer version if it is available)"
####    DIE=1
####  }
####}

grep "^AM_GNU_GETTEXT" $srcdir/configure.ac >/dev/null && {
  grep "sed.*POTFILES" $srcdir/configure.ac >/dev/null || \
  (gettext --version) < /dev/null > /dev/null 2>&1 || {
    echo
    echo "**Error**: You must have \`gettext' installed."
    echo "Get ftp://alpha.gnu.org/gnu/gettext-0.10.35.tar.gz"
    echo "(or a newer version if it is available)"
    DIE=1
  }
}

grep "^AM_GNOME_GETTEXT" $srcdir/configure.ac >/dev/null && {
  grep "sed.*POTFILES" $srcdir/configure.ac >/dev/null || \
  (gettext --version) < /dev/null > /dev/null 2>&1 || {
    echo
    echo "**Error**: You must have \`gettext' installed."
    echo "Get ftp://alpha.gnu.org/gnu/gettext-0.10.35.tar.gz"
    echo "(or a newer version if it is available)"
    DIE=1
  }
}

(automake --version) < /dev/null > /dev/null 2>&1 || {
  echo
  echo "**Error**: You must have \`automake' installed."
  echo "Get ftp://ftp.gnu.org/pub/gnu/automake-1.9.tar.gz"
  echo "(or a newer version if it is available)"
  DIE=1
  NO_AUTOMAKE=yes
}


# if no automake, don't bother testing for aclocal
test -n "$NO_AUTOMAKE" || (aclocal --version) < /dev/null > /dev/null 2>&1 || 
{
  echo
  echo "**Error**: Missing \`aclocal'.  The version of \`automake'"
  echo "installed doesn't appear recent enough."
  echo "Get ftp://ftp.gnu.org/pub/gnu/automake-1.9.tar.gz"
  echo "(or a newer version if it is available)"
  DIE=1
}

if test "$DIE" -eq 1; then
  exit 1
fi

case $CC in
xlc )
  am_opt=--include-deps;;
esac
	 echo "gettextize -f --copy --intl"
	 gettextize -f --copy --no-changelog
      if grep "^AM_PROG_LIBTOOL" configure.ac >/dev/null; then
        echo "Running libtoolize..."
        libtoolize --force --copy
      fi
	  echo "intltoolize"
	  intltoolize --force --copy --automake	  
      echo "Running aclocal --install ..."
	  if ! [ -d m4 ]; then
		  mkdir m4
	  fi
      aclocal -I m4 
      if grep "^AM_CONFIG_HEADER" configure.ac >/dev/null; then
        echo "Running autoheader..."
        autoheader
      fi
      echo "Running automake --gnu -c -f -a $am_opt ..."
      automake --add-missing --copy --gnu 
      echo "Running autoconf ..."
      autoconf

#conf_flags="--enable-maintainer-mode --enable-compile-warnings" 
#--enable-iso-c

./configure $*
