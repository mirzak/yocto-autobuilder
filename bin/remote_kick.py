#
# Example script on how to kick builds without using the web interface
#
'''
Created on June 1st 2016

__author__ = "Elizabeth Flanagan"
__copyright__ = "Copyright 2016, Linux Foundation"
__credits__ = ["Elizabeth Flanagan"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Elizabeth Flanagan"
__email__ = "pidge@toganlabs.com"
'''
import sys
import urllib2
import urllib
import cookielib

class RemoteBuild():
    MAX_RETRY = 3
    def __init__(self, server):
        self.server = server
        cookiejar = cookielib.CookieJar()
        self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

    def login(self, user, passwd):
        d = urllib.urlencode(dict(username=user, passwd=passwd))
        lurl = self.server + "/login"
        request = urllib2.Request(lurl, d)
        res = self.urlOpener.open(request).read()
        if res.find("The username or password you entered were not correct") > 0:
            raise Exception("Bad username or password")
        self.force_build(builder="nightly", reason='Remote kick of nightly')

    def force_build(self, builder, reason, **kw):
        """
        We'll need a kw for each bit of the build. These must be filled out.
        For now, just hard code it to get this working.
        """
        MAX_RETRY=3
        kw['branch_bitbake'] = 'master'
        kw['branch_eclipse-poky-kepler'] = 'kepler-master'
        kw['branch_eclipse-poky-luna'] = 'luna-master'
        kw['branch_eclipse-poky-mars'] = 'mars-master'
        kw['branch_oecore'] = 'master'
        kw['custom_create_eventlog'] = 'False'
        kw['custom_deploy_artifacts'] = 'False'
        kw['custom_is_milestone'] = 'False'
        kw['custom_milestone_number'] = ''
        kw['custom_poky_name'] = ''
        kw['custom_poky_number'] = ''
        kw['custom_prefered_kernel'] = 'linux-yocto'
        kw['custom_rc_number'] = ''
        kw['custom_release_me'] = 'False'
        kw['custom_send_email'] = 'False'
        kw['custom_yocto_number'] = ''
        kw['owner'] = 'foo@foo.com'
        kw['reason'] = ''
        kw['repo_bitbake'] = 'git://git.openembedded.org/bitbake'
        kw['repo_eclipse-poky-kepler'] = 'git://git.yoctoproject.org/eclipse-poky'
        kw['repo_eclipse-poky-luna'] = 'git://git.yoctoproject.org/eclipse-poky'
        kw['repo_eclipse-poky-mars'] = 'git://git.yoctoproject.org/eclipse-poky'
        kw['repo_meta-intel'] = 'git://git.yoctoproject.org/meta-intel'
        kw['repo_meta-minnow'] = 'git://git.yoctoproject.org/meta-minnow'
        kw['repo_meta-qt3'] = 'git://git.yoctoproject.org/meta-qt3'
        kw['repo_meta-qt4'] = 'git://git.yoctoproject.org/meta-qt4'
        kw['repo_oecore'] = 'git://git.openembedded.org/openembedded-core'
        kw['repo_poky'] = 'git://git.yoctoproject.org/poky'
        kw['ss_nightly'] = "{u'dummy': u'dummy'}"
        data_str = urllib.urlencode(kw)
        url = "%s/builders/%s/force" % (self.server, builder)
        request = urllib2.Request(url, data_str)
        file_desc = None
        for i in xrange(self.MAX_RETRY):
            try:
                file_desc = self.urlOpener.open(request)
                break
            except Exception as e:
                print >>sys.stderr, "error when doing force build", e
        if file_desc is None:
            print >>sys.stderr, "too many errors, giving up"
            return None
        print file_desc
        for line in file_desc:
            if 'Authorization Failed' in line:
                print "Authorization Failed"
                return

api = RemoteBuild("http://localhost:8010")
api.login("foo", "bar")

