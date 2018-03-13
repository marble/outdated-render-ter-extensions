import pdb
import os
import sys
import subprocess
import gzip
# from xml.sax import saxutils, handler, make_parser
from xml import sax

globalCounter = 0
bunch_at_a_time = 0

dest_path_to_extensions = '/home/mbless/public_html/typo3/extensions'


NL = '\n'
logfile_name = 'job.log.txt'
extensions_xml_gz_urls = [
    'http://typo3.org/fileadmin/ter/extensions.xml.gz',
    'http://ter.rz.tu-clausthal.de/ter/extensions.xml.gz',
    'http://ter.mittwald.de/ter/extensions.xml.gz',
    'http://ter.sitedesign.dk/ter/extensions.xml.gz',
    'http://ter.tue.nl/extensions.xml.gz',
    'http://mirror-typo3.vinehosting.com/ter/extensions.xml.gz',
    'http://ter.cablan.net/ter/extensions.xml.gz'
]
extensions_xml_gz_fname = 'extensions.xml.gz'
extensions_xml_fname = 'extensions.xml'
proceeding = True

class Logger:
    from datetime import datetime

    def __init__(self):
        import sys
        self.f2 = sys.stdout
        self.cnt = 0

    def open(self, fname):
        self.fname = fname
        self.f2 = file(fname, 'w')

    def close(self):
        if self.f2 and self.f2 != sys.stdout:
            self.f2.close()

    def msg(self, msg=None, nl=None, cnt=None, dt=True):
        if dt:
            self.f2.write('%s ' % (str(Logger.datetime.now())[:19]))
        if cnt:
            self.cnt += 1
            self.f2.write('\n%03d: ' % self.cnt)
        if (msg):
            self.f2.write(msg)
        if (nl):
            self.f2.write(nl)


class ContentHandlerExtensions(sax.handler.ContentHandler):

    def __init__(self, processor):
        sax.handler.ContentHandler.__init__(self)
        self.document = ['']
        self.extkey = ''
        self.version = ''
        self.content = ''
        self.process = processor

    def startDocument(self):
        self.document = ['']

    def startElement(self, name, attrs):
        self.document.append(name)
        if name == 'extension':
            self.extension = {}
            self.extension['versions'] = {}
            self.extension['extensionkey'] = attrs['extensionkey']
        elif name == 'version':
            self.version = {}
            self.version['version'] = attrs['version']

    def endElement(self, name):
        nameold = self.document.pop()
        if self.document[-1] == 'version':
            self.version[name] = self.content
        elif name == 'version':
            k = self.version['version']
            self.extension['versions'][k] = self.version
        elif name == 'extension':
            self.process(self.extension)

    def characters(self, content):
        self.content = content

    def ignorableWhitespace(self, content):
        pass

    def processingInstruction(self, target, data):
        pass


def extensionProcessor(D):
    global globalCounter, proceeding
    extkey = D['extensionkey']
    keys = sorted(D['versions'].keys())
    keys.reverse()
    for k in keys:
        if not bunch_at_a_time or globalCounter < bunch_at_a_time:
            version = k
            state = D['versions'][k]['state']
            source = 'http://typo3.org/extension-manuals/%s/%s/sxw/?no_cache=1' % (extkey, version)
            destdir = '%s/%s/%s' % (dest_path_to_extensions, extkey, version)
            outfile = '%s/manual.sxw' % destdir
            if not os.path.exists(destdir):
                os.makedirs(destdir)
                if 0:
                    log.msg("new: '%s'" % destdir, NL)
            if not os.path.exists(destdir):
                proceeding = False
                log.msg("abort: cannot create '%s'" % destdir, NL)
            if os.path.exists(outfile):
                if 0:
                    log.msg('ok, exists: %s ' % outfile, NL)
            else:
                cmd = '/usr/bin/wget -q --output-document=%s %s' % (outfile.replace('/',os.sep), source)
                log.msg(cmd, NL)
                retCode = subprocess.call(cmd, shell=True)
                if retCode != 0:
                    log.msg('bad: return code = %s' % retCode, NL)
                globalCounter += 1


if __name__ == '__main__':
    log = Logger()
    # log.open(logfile_name)
    log.msg('Starting ...', NL)

    if 1 and proceeding:
        fname = extensions_xml_gz_fname
        log.msg('task: provide %s' % fname,NL)
        if os.path.exists(fname):
            try:
                pass
                os.remove(fname)
            except:
                pass
        if os.path.exists(fname):
            log.msg("abort: cannot remove '%s'" % fname, NL)
            proceeding = False

    if 1 and proceeding:
        wget_cmd = '/usr/bin/wget -q --output-document=%s ' % extensions_xml_gz_fname
        for url in extensions_xml_gz_urls:
            cmd = wget_cmd + url
            log.msg(cmd, NL)
            retCode = subprocess.call(cmd, shell=True)
            if retCode == 0:
                log.msg('ok.', NL)
                break
            else:
                log.msg('bad: return code: %s' % retCode, NL)
        else:
            proceeding = False
            log.msg('abort: could not fetch the file', NL)

    if 1 and proceeding:
        # unpack
        f1 = gzip.GzipFile(extensions_xml_gz_fname)
        f2 = file(extensions_xml_fname, 'w')
        for line in f1:
            f2.write(line)
        f2.close()
        f1.close()
  
    if proceeding:
        # parse and process
        parser = sax.make_parser()
        parser.setContentHandler(ContentHandlerExtensions(extensionProcessor))
        parser.parse(extensions_xml_fname)

log.msg('task: close logfile', NL)
log.msg('Done.', NL)
log.close()
