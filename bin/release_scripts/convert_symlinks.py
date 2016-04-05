import os
import optparse
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
    print "MACHINES: %s" %MACHINES
    print
    return


def get_list(dirname):
    dirlist = os.listdir(dirname)
    dirlist.sort()
    return dirlist

def split_thing(thing, marker):
    filebits = thing.split(marker)
    return filebits

def rejoin_thing(thing, marker):
    filebits = marker.join(thing)
    return filebits


def convert_symlinks(dirname):
    thing = os.path.split(dirname)[1]
    if thing == "qemu":
        dirlist = get_list(dirname)
        for dir in dirlist:
            qemu_dir = os.path.join(MACHINES, dirname, dir)
            print "Converting symlinks in %s" %qemu_dir
            convert_symlinks(qemu_dir)
    else:
        print "Converting symlinks in %s" %dirname
        link_list = []
        for root, dirs, files in os.walk(dirname, topdown=True):
            for name in files:
                filename = (os.path.join(root, name))
                if os.path.islink(filename):
                    src_file = os.path.realpath(filename)
                    link_list.append([filename, src_file])
        for line in link_list:
            os.remove(line[0])
            try:
               copyfile(line[1], line[0])
            except IOError:
                print "Error: %s is missing or isn\'t a real file" %line[1]
            else:
                print line[0]
        for line in link_list:
            if os.path.exists(line[1]):
               os.remove(line[1])
    print
    return


def nuke_cruft(dirname, ext_list):
    thing = os.path.split(dirname)[1]
    if thing == "qemu":
        dirlist = get_list(dirname)
        for dir in dirlist:
            qemu_dir = os.path.join(MACHINES, dirname, dir)
            nuke_cruft(qemu_dir, CRUFT_LIST)
    else:
        foo = dirname.find("p1022")
        if foo == -1:
            # NOT P1022ds
            for ext in ext_list:
                print "Deleting %s files" %ext
                os.system("rm -f %s/%s" %(dirname, ext))
        else:
            # IS P1022ds
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
            convert_symlinks(dirname)
    else:
        print "Graciously declining to do anything. I don't know what %s is." %RELEASE_DIR


