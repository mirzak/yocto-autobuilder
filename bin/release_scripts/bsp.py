'''
Created on Mar 20, 2016

__author__ = "Tracy Graydon"
__copyright__ = "Copyright 2016, Intel Corp."
__credits__ = ["Tracy Graydon"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Tracy Graydon"
__email__ = "tracy.graydon@intel.com"
'''

import os
import optparse
import sys
import hashlib
import glob
import os.path
import shutil
from shutil import rmtree, copyfile
from subprocess import call

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

def purge_unloved():
    print
    print "Purging unwanted directories..."
    for target in UNLOVED:
        target = target.rstrip()
        print "Deleting: %s/%s" %(RELEASE_DIR, target)
        os.system('rm -rf %s/%s' %(RELEASE_DIR, target))
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

def get_md5sum(path, blocksize = 4096):
    f = open(path, 'rb')
    md5sum = hashlib.md5()
    buffer = f.read(blocksize)
    while len(buffer) > 0:
        md5sum.update(buffer)
        buffer = f.read(blocksize)
    f.close()
    return md5sum.hexdigest()

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

def find_dupes(dirname, platform):
    print "\nLooking for duplicate files in %s" %dirname
    file_list = []
    md5sum_list = []
    for root, dirs, files in os.walk(dirname, topdown=True):
        for name in files:
            filename = (os.path.join(root, name))
            md5sum = get_md5sum(filename)
            file_list.append((filename, md5sum))
            md5sum_list.append(md5sum)
    s=set(md5sum_list)
    d=[]
    for x in file_list:
        if x[1] in s:
            s.remove(x[1])
        else:
            d.append(x[1])
    for dupe in d:
        for tup in file_list:
            if tup[1] == dupe:
                dupe_name = split_thing(tup[0],"/")
                filename = dupe_name[-1]
                if filename.find(platform) == -1:
                    print "Deleting %s" %tup[0]
                    os.remove(tup[0])
    return

def make_bsps(bsp_list, bsp_dir):
    print "\nCreating bsps.....\n"
    if not os.path.exists(bsp_dir):
        os.mkdir(bsp_dir)
    else:
        print "BSP tarball dir exists! Skipping BSP creation."
        return
    poky_blob = os.path.join(RELEASE_DIR, POKY_TARBALL)
    blob_dir = split_thing(POKY_TARBALL, ".")
    blob_dir = rejoin_thing(blob_dir[:-2], ".")
    os.chdir(bsp_dir)
    for dirname in bsp_list:
        platform_dir = os.path.join(MACHINES, dirname)
        if os.path.exists(platform_dir):
            if not os.path.exists(dirname):
                print "Creating %s bsp dir" %dirname
                os.mkdir(dirname)
            target = os.path.join(dirname, POKY_TARBALL)
            oldblob = POKY_TARBALL
            chunks = split_thing(oldblob, "-")
            chunks[0] = dirname
            new_blob = rejoin_thing(chunks, "-")
            print "BSP tarball: %s" %new_blob
            new_dir = split_thing(blob_dir, "-")
            new_dir[0] = dirname
            new_dir = rejoin_thing(new_dir, "-")
            bin_dir = os.path.join(new_dir, "binary")
            copyfile(poky_blob, target)
            os.chdir(dirname)
            print "Unpacking poky tarball."
            os.system("tar jxf %s" %POKY_TARBALL)
            shutil.move(blob_dir, new_dir)
            os.remove(POKY_TARBALL)
            if not os.path.exists(bin_dir):
                os.mkdir(bin_dir)
            print "Getting binary files"
            os.system("rsync -arl %s/%s/ %s" %(MACHINES, dirname, bin_dir))
            bsp_bin = os.path.join(bsp_dir, dirname, bin_dir)
            convert_symlinks(bin_dir)
            nuke_cruft(bin_dir, BSP_JUNK)
            bsp_path = os.path.join(bsp_dir, dirname, bin_dir)
            find_dupes(bsp_path, dirname)
            print "Creating BSP tarball"
            os.system("tar jcf %s %s" %(new_blob, new_dir))
            rmtree(new_dir)
            print "Generating the md5sum."
            os.system("md5sum %s > %s.md5sum" %(new_blob, new_blob))
            print "Copying %s BSP to platform dir" %dirname
            os.system("mv * %s" %platform_dir)
            os.chdir(bsp_dir)
        print
    os.chdir(RELEASE_DIR)
    rmtree(bsp_dir)
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

def release_type(build_id):
    build_id = build_id.lower()
    RC = split_thing(build_id, ".")[-1]
    foo = RC.find("rc")
    if foo == -1:
        print "%s doesn't appear to be a valid RC candidate. Check your args." %build_id
        print "Please use -h or --help for options."
        sys.exit()
    chunks = split_thing(build_id, ".") # i.e. split yocto-2.1_m1.rc1
    chunks.pop()
    chunks[1] = chunks[1].upper()
    RELEASE = rejoin_thing(chunks, ".")  # i.e. yocto-2.1_m1
    REL_ID = split_thing(RELEASE, "-")[-1].upper()
    RC_DIR = rejoin_thing([RELEASE, RC], ".")
    relstring = split_thing(REL_ID, "_")
    if len(relstring) == 1:
        thing = split_thing(relstring[0], ".")
        if len(thing) == 3:
            REL_TYPE = "point"
        elif len(thing) == 2:
            REL_TYPE = "major"
    else:
        print "We don't generate release notes for Milestone releases."
        sys.exit()

    if not (RELEASE and RC and REL_ID and REL_TYPE):
        print "Can't determine the release type. Check your args."
        print "You gave me: %s" %options.build
        sys.exit()

    var_dict = {'RC': RC, 'RELEASE': RELEASE, 'REL_ID': REL_ID, 'RC_DIR': RC_DIR, 'REL_TYPE': REL_TYPE};
    return var_dict

if __name__ == '__main__':

    os.system("clear")
    print

    VHOSTS = "/srv/www/vhosts"
    AB_BASE = os.path.join(VHOSTS, "autobuilder.yoctoproject.org/pub/releases")
    DL_BASE = os.path.join(VHOSTS, "downloads.yoctoproject.org/releases/yocto")
    ADT_BASE = os.path.join(VHOSTS, "adtrepo.yoctoproject.org")

    # List of the files in machines directories that we delete from all releases
    CRUFT_LIST = ['*.md5sum', '*.tar.gz', '*.iso']
    # List of the platforms for which we want to generate BSP tarballs. Major and point releases.
    BSP_LIST = ['beaglebone', 'edgerouter', 'genericx86', 'genericx86-64', 'mpc8315e-rdb', 'p1022ds']
    # List of files we do not want to include in the BSP tarballs.
    BSP_JUNK = ['*.manifest', '*.tar.bz2', '*.tgz', '*.iso', '*.md5sum', '*.tar.gz', '*-dev-*', '*-sdk-*']

    parser = optparse.OptionParser()
    parser.add_option("-i", "--build-id",
                      type="string", dest="build",
                      help="Required. Release candidate name including rc#. i.e. yocto-2.0.rc1, yocto-2.1_M1.rc3, etc.")
    parser.add_option("-b", "--branch",
                      type="string", dest="branch",
                      help="Required for Major and Point releases. i.e. daisy, fido, jethro, etc.")
    parser.add_option("-p", "--poky-ver",
                      type="string", dest="poky",
                      help="Required for Major and Point releases. i.e. 14.0.0")

    (options, args) = parser.parse_args()

    if not (options.build and options.poky and options.branch):
        print "You need to specify the RC candidate, the poky version and the branch."
        print "Please use -h or --help for options."
        sys.exit()

    REL_TYPE = ""
    POKY_VER = options.poky
    BRANCH = options.branch
    VARS = release_type(options.build)
    RC = VARS['RC']
    RELEASE = VARS['RELEASE']
    REL_ID = VARS['REL_ID']
    RC_DIR = VARS['RC_DIR']
    REL_TYPE = VARS['REL_TYPE']
    RC_SOURCE = os.path.join(AB_BASE, RC_DIR)
    RELEASE_DIR = os.path.join(AB_BASE, RELEASE)

    # Show and Tell
    listdict = dict.keys(VARS)
    for line in listdict:
        print "%s: %s" %(line, VARS[line])
    print "BRANCH: %s" %BRANCH
    print "POKY_VER: %s" %POKY_VER

    RELEASE_DIR = os.path.join(AB_BASE, RELEASE)
    DL_DIR = os.path.join(DL_BASE, RELEASE)
    MACHINES = os.path.join(RELEASE_DIR, "machines")
    BSP_DIR = os.path.join(RELEASE_DIR, 'bsptarballs')
    POKY_TARBALL = "poky-" + BRANCH + "-" + POKY_VER + ".tar.bz2"

    print "Generating the BSP tarballs."
    make_bsps(BSP_LIST, BSP_DIR)
