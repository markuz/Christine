#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

REQUIRED_AUTOMAKE_VERSION=1.7

PKG_NAME="Christine"

echo -n "+ check for build tools"
if test ! -z $NOCHECK; then echo ": skipped version checks"; else  echo; fi
G=`intltoolize --version`
if "$G" == "" ; then
	echo "There is no intltoolize"; 
	echo "G: $G";
	exit 0; 
else 
	echo "intltoolize... OK"
fi

(test -f $srcdir/configure.ac \
## put other tests here
) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level $PKG_NAME directory"
    exit 1
}

echo "gettextize -f --copy"
gettextize -f --copy
echo "intltoolize --force --copy --automake"
intltoolize --force --copy --automake
echo "aclocal -I m4"
aclocal -I m4
echo "automake --add-missing --copy --gnu"
automake --add-missing --copy --gnu
echo "autoconf"
autoconf

if test x$NOCONFIGURE = x; then
  echo Running $srcdir/configure $conf_flags "$@" ...
    $srcdir/configure $conf_flags "$@" \
	  && echo Now type \`make\' to compile. || exit 1
  else
    echo Skipping configure process.
fi

#echo "sh configure --prefix=/usr"
#sh configure --prefix=/usr
#echo "make"
#make 

