#!/usr/bin/python

import os
import optparse
import sys
import hashlib
import glob
import os.path
import shutil
from shutil import rmtree, copyfile
from subprocess import call


def split_thing(thing, marker):
    filebits = thing.split(marker)
    return filebits

def rejoin_thing(thing, marker):
    filebits = marker.join(thing)
    return filebits

def get_md5sum(path, blocksize = 4096):
    f = open(path, 'rb')
    md5sum = hashlib.md5()
    buffer = f.read(blocksize)
    while len(buffer) > 0:
        md5sum.update(buffer)
        buffer = f.read(blocksize)
    f.close()
    return md5sum.hexdigest()


def gen_md5sum(dirname):
    print
    print "Generating md5sums for files in %s...." %dirname
    for root, dirs, files in os.walk(dirname, topdown=True):
        for name in files:
            filename = (os.path.join(root, name))
            md5sum = get_md5sum(filename)
            md5_file = ".".join([filename, 'md5sum'])
            md5str = md5sum + " " + name
            print md5str
            f = open(md5_file, 'w')
            f.write(md5str)
            f.close()
    return

def print_vars():
    print "AB_BASE: %s" %AB_BASE
    print "RELEASE_DIR: %s" %RELEASE_DIR
    print "MACHINES: %s" %MACHINES
    print
    return


if __name__ == '__main__':

    os.system("clear")
    print

    # This is for testing convenience
    HOME_BASE = "/home/tgraydon/work/release"
    AB_BASE = HOME_BASE

    # This is the legit set of vars used for production release
    #VHOSTS = "/srv/www/vhosts"
    #AB_BASE = os.path.join(VHOSTS, "autobuilder.yoctoproject.org/pub/releases")

    parser = optparse.OptionParser()
    parser.add_option("-d", "--dirname",
                      type="string", dest="dirname",
                      help="Required. Name of the staging dir for which to generate machine md5ums. i.e. yocto-2.0, yocto-2.1_M1, etc.")

    (options, args) = parser.parse_args()

    if options.dirname:
        if options.dirname.find("rc") == -1 and options.dirname.find("RC") == -1:
            print options.dirname
            RELEASE_DIR = os.path.join(AB_BASE, options.dirname)
            MACHINES = os.path.join(RELEASE_DIR, "machines")
        else:
            print "Hey! You can't touch an RC candidate! Check your args!"
            sys.exit()
    else:
        print "Huh? Check your args."
        print "Please use -h or --help for options."
        sys.exit()

    print_vars()
    if os.path.exists(MACHINES):
        gen_md5sum(MACHINES)
    else:
        print "Graciously declining to do anything. I don't know what %s is." %RELEASE_DIR


