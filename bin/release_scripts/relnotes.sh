#!/bin/bash

# NOTE! This script will blissfully clobber any pre-existing poky repos, 
# previous release notes with same filename, etc. 
#
# This is a quick and ugly script to generate the release notes draft.
#
# Usage: ./relnotes.sh <release_ID> <rc#> <branch> <poky-ver>
# i.e. ./relnotes.sh yocto-2.0.1 rc6 jethro 14.0.1
#
# Currently the revision in the git log portion is hard coded. You 
# will want to change accordingly! 
# i.e. git log --pretty=format:"%s" yocto-2.0..HEAD |grep CVE >> $HOME/CVE;
# Change the yocto-2.0 bit to whatever it needs to be for the given release.



clear
REL_ID=$1
RC=$2
BRANCH=$3
POKY_VER=$4
RELEASE=$REL_ID
VHOSTS="/srv/www/vhosts"
AB_BASE="$VHOSTS/autobuilder.yoctoproject.org/pub/releases"
DL_BASE="$VHOSTS/downloads.yoctoproject.org/releases"
RC_SOURCE="$AB_BASE/$RELEASE.$RC"
RELEASE_DIR="$AB_BASE/$RELEASE"
MACHINES="$RELEASE_DIR/machines"
HOME=~/work/release
echo "REL_ID: $REL_ID"
echo "RC: $RC"
echo "BRANCH: $BRANCH"
echo "POKY_VER: $POKY_VER"
echo "RELEASE: $RELEASE"
echo "AB_BASE: $AB_BASE"
echo "DL_BASE: $DL_BASE"
echo "RC_SOURCE: $RC_SOURCE"
echo "RELEASE_DIR: $RELEASE_DIR"
echo "MACHINES: $MACHINES"
echo

if [[ -e $HOME/RELEASENOTES.$RELEASE ]]; then
    rm -v $HOME/RELEASENOTES.$RELEASE
fi
if [[ -e $HOME/CVE ]]; then
    rm -v $HOME/CVE
fi
if [[ -e $HOME/FIXES ]]; then
    rm -v $HOME/FIXES
fi
if [[ -d $HOME/poky ]]; then
    rm -rvf $HOME/poky
fi

for x in `ls $RELEASE_DIR/*.bz2.md5sum | grep -v "\-fsl" | grep -v "\-ppc"`; do 
   layer=`basename $x | sed 's/\-'"$BRANCH"'\-'"$POKY_VER"'.tar.bz2.md5sum//g'`; 
   tarball=`basename $x |sed 's/\.md5sum//g'`; 
   ghash=`ls $RELEASE_DIR/$layer*.bz2 | grep -v $BRANCH | sed 's/'"$layer"'-//g' | sed 's/.tar.bz2//g'`;
   ghash=`basename $ghash`
   echo "Release Name: " $layer-$BRANCH-$POKY_VER; 
   echo "Branch: $BRANCH"; 
   echo "Tag: $BRANCH-$POKY_VER"; 
   echo "Hash: " $ghash; 
   echo "md5: `cat $RELEASE_DIR/$tarball.md5sum`"; 
   echo "Download Locations:"; 
   echo "http://downloads.yoctoproject.org/releases/yocto/$RELEASE/$tarball"; 
   echo "http://mirrors.kernel.org/yocto/yocto/$RELEASE/$tarball"; echo ""; 
done >> $HOME/RELEASENOTES.$RELEASE

git clone git://git.yoctoproject.org/poky;
cd poky; 
git checkout $BRANCH; 
echo -e "\n-------\nSecurity Fixes\n-------" >> $HOME/CVE;
git log --pretty=format:"%s" yocto-2.0..HEAD |grep CVE >> $HOME/CVE; 
echo -e "\n-------\nFixes\n-------" >> $HOME/FIXES; 
git log --pretty=format:"%s" yocto-2.0..HEAD |grep -v CVE >> $HOME/FIXES; 
cat $HOME/CVE >> $HOME/RELEASENOTES.$RELEASE; cat $HOME/FIXES >> $HOME/RELEASENOTES.$RELEASE
cd $HOME



