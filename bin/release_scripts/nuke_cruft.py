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

def get_list(dirname):
    dirlist = os.listdir(dirname)
    dirlist.sort()
    return dirlist

def nuke_cruft(dirname, ext_list):
    #TODO: handle corner case of multiple dte stamps in machines dir
    #print "Nuking unwanted files in %s" %dirname
    thing = os.path.split(dirname)[1]
    #print thing
    if thing == "qemu":
        print "Bada Bing. Qemu!"
        dirlist = get_list(dirname)
        #print dirlist
        for dir in dirlist:
            qemu_dir = os.path.join(MACHINES, dirname, dir)
            #print qemu_dir
            nuke_cruft(qemu_dir, CRUFT_LIST)
    else:
        foo = dirname.find("p1022")
        if foo == -1:
            # NOT P1022ds
            for ext in ext_list:
                print "Deleting %s files" %ext
                os.system("rm -f %s/%s" %(dirname, ext))
        else:
            # IS p1022ds
            for ext in ext_list:
                if ext != "*.tar.gz":
                    print "Deleting %s files" %ext
                    os.system("rm -f %s/%s" %(dirname, ext))
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

    # List of the files in machines directories that we delete from all releases
    CRUFT_LIST = ['*.md5sum', '*.tar.gz', '*.iso']
 
    parser = optparse.OptionParser()
    parser.add_option("-d", "--dirname",
                      type="string", dest="dirname",
                      help="Required. Name of the staging dir. i.e. yocto-2.0, yocto-2.1_M1, etc.")
                     
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
         
    if os.path.exists(MACHINES):
        dirlist = get_list(MACHINES)
        for dirname in dirlist:
            dirname = os.path.join(MACHINES, dirname)
            nuke_cruft(dirname, CRUFT_LIST)
    else:
        print "Graciously declining to do anything. I don't know what %s is." %RELEASE_DIR


