#!/usr/bin/python

import os
import optparse
import argparse
import sys
import hashlib
import glob
import os.path
import shutil
from shutil import rmtree, copyfile
from subprocess import call

def print_vars():
    print "RELEASE: %s" %RELEASE
    print "REL_TYPE: %s" %REL_TYPE
    print "RC_DIR: %s" %RC_DIR
    print "REL_ID: %s" %REL_ID
    print "RC: %s" %RC
    if MILESTONE != "":
        print "Milestone: %s" %MILESTONE
    if POKY_VER != "":
        print "POKY_VER: %s" %POKY_VER
    if BRANCH:
        print "BRANCH: %s" %BRANCH

    #print "HOME_BASE: %s" %HOME_BASE
    #print "AB_BASE: %s" %AB_BASE
    #print "DL_BASE: %s" %DL_BASE
    #print "ADT_SRC: %s" %ADT_SRC
    #print "ADT_BASE: %s" %ADT_BASE
    #print "RC_SOURCE: %s" %RC_SOURCE
    #print "ECLIPSE_DIR: %s" %ECLIPSE_DIR
    #print "PLUGIN_DIR: %s" %PLUGIN_DIR
    #print "RELEASE_DIR: %s" %RELEASE_DIR
    #print "MACHINES: %s" %MACHINES
    #print "ADT_DIR: %s" %ADT_DIR
    #print "TARBALL_DIR: %s" %TARBALL_DIR
    #print "BUILD_APP_DIR: %s" %BUILD_APP_DIR
    #print "UNLOVED: %s" %UNLOVED
    #print "CRUFT_LIST: %s" %CRUFT_LIST
    print
    return

def sanity_check(source, target):
    if not os.path.exists(source):
       print
       print "SOURCE dir %s does NOT EXIST." %source
       print
       sys.exit()
    if not os.listdir(source):
       print
       print "SOURCE dir %s is EMPTY" %source
       print
    if os.path.exists(target):
       print
       print "I can't let you do it, Jim. The TARGET directory %s exists." %target
       print
       sys.exit()
    return

def sync_it(source, target, exclude_list):
    print "SOURCE: %s" %source
    print "Target: %s" %target
    #sanity_check(source, target)
    source = source + "/"
    #os.mkdir("%s" %target)
    if exclude_list:
        exclusions = ['--exclude=%s' % x.strip() for x in exclude_list]
        print "Exclusions: %s" %exclusions
        print
        exclude = "--exclude=" + os.path.join(RELEASE_DIR, exclude_list[0])
        #print "Exclude: %s" %exclude
        length = len(exclude_list)
        for i in range(1, length):
            #print exclude_list[i]
            exclude = exclude + " " + "--exclude=" + os.path.join(RELEASE_DIR, exclude_list[i])
        print "Exclude: %s" %exclude
        command = "rsync -avrl " + exclude + source + " " + target
        #print command
        #os.system (command)
        os.system("rsync -avrl --exclude=deb --exclude=rpm --exclude=ptest --exclude=adt-installer-QA '%s' '%s'" %(source, target))
    else:
        print "No exclude list"
        #os.system("rsync -avrl '%s' '%s'" %(source, target))

def split_thing(thing, marker):
    filebits = thing.split(marker)
    return filebits

def rejoin_thing(thing, marker):
    filebits = marker.join(thing)
    return filebits


if __name__ == '__main__':
    
    os.system("clear")
    print
    
    parser = optparse.OptionParser()
    parser.add_option("-i", "--build-id", type="string", dest="build", help="build id of release including rc#. i.e. yocto-2.0.rc1, yocto-2.1_M1.rc3, etc.")
    parser.add_option("-b", "--branch", type="string", dest="branch", help="branch for the release. i.e. daisy, fido, jethro, etc.")
    parser.add_option("-p", "--poky-ver", type="string", dest="poky", help="poky version for the release. i.e. 14.0.0")

    (options, args) = parser.parse_args()
 
    REL_TYPE = ""
    MILESTONE = ""
    POKY_VER = ""
    BRANCH = ""

    if options.build:
        chunks = split_thing(options.build, ".")
        chunks.pop()
        RELEASE = rejoin_thing(chunks, ".")  # yocto-2.1_M1
        rel_thing = split_thing(options.build, "-")
        #prefix = rel_thing[0]
        #print "Prefix: %s" %prefix
        RC = split_thing(options.build, ".")[-1].lower()
        RC_DIR = RELEASE + "." + RC
        REL_ID = split_thing(RELEASE, "-")[-1]
        milestone = split_thing(REL_ID, "_")
        if len(milestone) == 1:
            thing = split_thing(milestone[0], ".")
            if len(thing) == 3:
                REL_TYPE = "point"
            elif len(thing) == 2:
                REL_TYPE = "major"
            if options.poky and options.branch:
                POKY_VER = options.poky
                BRANCH = options.branch
            else:
                print "You can't have a major or point release without a branch and a poky version. Check your args."
                print_vars()
                sys.exit()
        else:
            MILESTONE = milestone.pop()
            REL_TYPE = "milestone"
    else:
        print "Please use -h or --help for options."
        sys.exit()
    
    # This is for testing convenience
    HOME_BASE = "/home/tgraydon/work/release"
    AB_BASE = HOME_BASE
    DL_BASE = HOME_BASE
    ADT_SRC = os.path.join(HOME_BASE, "adtrepo-dev")
    ADT_BASE = os.path.join(HOME_BASE, "adt")

    # This is the legit set of vars used for production release
    #VHOSTS = "/srv/www/vhosts"
    #AB_BASE = os.path.join(VHOSTS, "autobuilder.yoctoproject.org/pub/releases")
    #DL_BASE = os.path.join(VHOSTS, "downloads.yoctoproject.org/releases")
    #ADT_SRC = os.path.join(VHOSTS, "adtrepo-dev")
    #ADT_BASE = os.path.join(VHOSTS, "adtrepo.yoctoproject.org")

    RC_SOURCE = os.path.join(AB_BASE, RC_DIR)
    PLUGIN_DIR = os.path.join(DL_BASE, "eclipse-plugin", REL_ID)
    RELEASE_DIR = os.path.join(AB_BASE, RELEASE)
    MACHINES = os.path.join(RELEASE_DIR, "machines")
    BSP_DIR = os.path.join(RELEASE_DIR, 'bsptarballs')
    ADT_DIR = os.path.join(ADT_BASE, REL_ID)
    TARBALL_DIR = os.path.join(RELEASE_DIR, "tarballs")
    POKY_TARBALL = "poky-" + POKY_VER + ".tar.bz2"
    ECLIPSE_DIR = os.path.join(RELEASE_DIR, "eclipse-plugin")
    BUILD_APP_DIR = os.path.join(RELEASE_DIR, "build-appliance")
    UNLOVED = ['rpm', 'deb', 'ptest', 'adt-installer-QA']
    CRUFT_LIST = ['*.md5sum', '*.tar.gz', '*.iso']
    BSP_LIST = ['beaglebone', 'edgerouter', 'genericx86', 'genericx86-64', 'mpc8315e-rdb', 'p1022ds']
    BSP_JUNK = ['*.manifest', '*.tar.bz2', '*.tgz', '*.iso', '*.md5sum', '*.tar.gz', '*-dev-*', '*-sdk-*']

    print_vars()

    sync_it(RC_SOURCE, RELEASE_DIR, UNLOVED)

