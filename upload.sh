#!/bin/bash
echo "\$BWLIMIT=$BWLIMIT"
echo "\$VERSION=$VERSION"
rsync $BWLIMIT -P -e ssh $* thesystems,christine@frs.sourceforge.net:/home/frs/project/c/ch/christine/christine/$VERSION/

