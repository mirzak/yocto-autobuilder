'''
Created on March 18, 2015

__author__ = "Elizabeth 'pidge' Flanagan"
__copyright__ = "Copyright 2015, Intel Corp."
__credits__ = ["Elizabeth Flanagan"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Elizabeth Flanagan"
__email__ = "elizabeth.flanagan@intel.com"
'''

from buildbot.steps.shell import ShellCommand
import os
from twisted.python import log
import ast, json

class AddKernelProps(ShellCommand):
    haltOnFailure = False
    flunkOnFailure = True
    name = "AutoConfKernOverR"
    def __init__(self, factory, argdict=None, **kwargs):
        self.machine=""
        self.distro="poky"
        self.kstring = "pn-linux-yocto"
        self.kwargs = kwargs
        for k, v in argdict.iteritems():
            if type(v) is bool:
                setattr(self, k, str(v))
            else:
                setattr(self, k, v)
        self.description = "Add Kernel Bits to Auto Configuration"
        ShellCommand.__init__(self, **kwargs)

    def start(self):
        self.distro = self.getProperty("DISTRO")
        self.machine = self.getProperty("MACHINE")
        kmeta = self.getProperty("custom_kmeta")
        kbranch = self.getProperty("custom_kbranch")
        srcrev_meta = self.getProperty("custom_srcrev_meta")
        srcrev_machine = self.getProperty("custom_srcrev_machine")
        srcuri_meta = self.getProperty("custom_srcuri_meta")
        srcuri_machine = self.getProperty("custom_srcuri_machine")
        fout = ""
        if self.distro == "poky-rt":
            self.kstring = "pn-linux-yocto-rt"
        if srcrev_machine != "" and str(srcrev_machine) != "None":
            fout += "SRCREV_machine_%s_%s = \"%s\"\n" % (self.machine, self.kstring, srcrev_machine)
        if srcrev_meta != "" and str(srcrev_meta) != "None":
            fout += "SRCREV_meta_%s_%s = \"%s\"\n" % (self.machine, self.kstring, srcrev_meta)
        if kmeta != "" and str(kmeta) != "None":
            fout += 'KMETA_%s_%s = \"%s\"\n' % (self.machine, self.kstring, kmeta)
        if srcuri_meta != "" and str(srcuri_meta) != "None":
            fout += "SRC_URI_%s_%s += \"%s;bareclone=1;branch=${KMETA};type=kmeta;name=meta\"\n" % (self.machine, self.kstring, srcuri_meta)
        if kbranch != "" and str(kbranch) != "None":
            fout += 'KBRANCH_%s_%s = \"%s\"\n' % (self.machine, self.kstring, kbranch)
        if srcuri_machine != "" and str(srcuri_machine) != "None":
            fout += "SRC_URI_%s_%s += \"%s;bareclone=1;branch=${KBRANCH};type=machine;name=machine\"\n" % (self.machine, self.kstring, srcuri_machine)
        self.command = ["sh", "-c", "printf '" + fout + "'>> ./build/conf/auto.conf"]
        ShellCommand.start(self)
