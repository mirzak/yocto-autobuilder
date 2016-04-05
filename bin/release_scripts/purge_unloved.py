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
    print "AB_BASE: %s" %AB_BASE
    print "RELEASE_DIR: %s" %RELEASE_DIR
    print
    return

def purge_unloved():
    print
    print "Purging unwanted directories..."
    for target in UNLOVED:
        target = target.rstrip()
        print "Deleting: %s/%s" %(RELEASE_DIR, target)
        os.system('rm -rf %s/%s' %(RELEASE_DIR, target))
    return

def split_thing(thing, marker):
    filebits = thing.split(marker)
    return filebits

def rejoin_thing(thing, marker):
    filebits = marker.join(thing)
    return filebits

if __name__ == '__main__':

    os.system("clear")
    print

    # This is for testing convenience
    HOME_BASE = "/home/tgraydon/work/release"
    AB_BASE = HOME_BASE
    DL_BASE = os.path.join(HOME_BASE, "downloads")
    ADT_DEV = os.path.join(HOME_BASE, "adtrepo-dev")
    ADT_BASE = os.path.join(HOME_BASE, "adtrepo")

    # This is the legit set of vars used for production release
    #VHOSTS = "/srv/www/vhosts"
    #AB_BASE = os.path.join(VHOSTS, "autobuilder.yoctoproject.org/pub/releases")
    #DL_BASE = os.path.join(VHOSTS, "downloads.yoctoproject.org/releases")
    #ADT_SRC = os.path.join(VHOSTS, "adtrepo-dev")
    #ADT_BASE = os.path.join(VHOSTS, "adtrepo.yoctoproject.org")

    # List of the directories we delete from all releases
    UNLOVED = ['rpm', 'deb', 'ptest', 'adt-installer-QA']

    parser = optparse.OptionParser()
    parser.add_option("-d", "--dirname",
                      type="string", dest="dirname",
                      help="Required. Name of the staging dir you want to clean up. i.e. yocto-2.0, yocto-2.1_M1, etc.")

    (options, args) = parser.parse_args()

    if options.dirname:
        # Figure out the release name, type of release, and generate some vars, do some basic validation
        if options.dirname.find("rc") == -1 and options.dirname.find("RC") == -1:
            print options.dirname
            RELEASE_DIR = os.path.join(AB_BASE, options.dirname)
        else:
            print "Hey! You can't touch an RC candidate! Check your args!"
            sys,exit()
    else:
        print "Huh? Check your args."
        print "Please use -h or --help for options."
        sys.exit()

    print_vars()
    if os.path.exists(RELEASE_DIR):
        purge_unloved()
    else:
        print "Graciously declining to delete anything. I don't know what %s is." %RELEASE_DIR
