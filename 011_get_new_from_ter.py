#! /usr/bin/python

# mb, 2012-05-07, 2012-05-17
# ((is running as cronjob)) no, not yet

import os
import sys
import subprocess
import gzip
import zipfile
from xml import sax
import logger
import copyclean
import ooxhtml2rst_work_in_progress as ooxhtml2rst
import urllib
import time

ospe = os.path.exists
ospj = os.path.join

NL = '\n'
extensions_xml_gz_urls = [
    'http://typo3.org/fileadmin/ter/extensions.xml.gz',
    'http://ter.rz.tu-clausthal.de/ter/extensions.xml.gz',
    'http://ter.mittwald.de/ter/extensions.xml.gz',
    'http://ter.sitedesign.dk/ter/extensions.xml.gz',
    'http://ter.tue.nl/extensions.xml.gz',
    'http://mirror-typo3.vinehosting.com/ter/extensions.xml.gz',
    'http://ter.cablan.net/ter/extensions.xml.gz'
]

simulate = True

cwd = os.getcwd()
cwd = os.path.abspath(os.path.dirname(sys.argv[0]))
tempdir = ospj(cwd, 'temp2')
extensions_xml_gz_fname = 'extensions.xml.gz'
extensions_xml_fname = 'extensions.xml'
proceeding = True
mockup_uno = False
globalCountExtensions = 0
globalIndexPageNeedsRebuild = False
globalTimeStr = None
manualIsNotAvailableFile = 'manual-is-not-available.txt'
sxw2htmlConversionErrorFile = 'sxw2html-conversion-error.txt'
url_of_extensions = 'https://docs.typo3.org/typo3cms/extensions'

absPathToTemplate = '/home/mbless/HTDOCS/render-ter-extensions/template.txt' 

dest_path_to_extensions = '/home/mbless/public_html/typo3/extensions'
if not os.path.isdir(dest_path_to_extensions):
    dest_path_to_extensions = r'U:\htdocs\LinuxData200\srv123-typo3-org\remote\public_html\typo3\extensions'
    mockup_uno = True
if not os.path.isdir(dest_path_to_extensions):
    dest_path_to_extensions = ''
if not os.path.isdir(dest_path_to_extensions):
    log.msg("abort: Don't know the path to the extensions.", NL)
    sys.exit(2)
   
if not mockup_uno:
    import documentconverter as dc
    converter = dc.DocumentConverter()    

# errorfilename = 'sxw2html-conversion-error.txt'
stylesheet_path = 'https://docs.typo3.org/css/typo3_docutils_styles.css'

usr_bin_python = '/usr/bin/python'
rst2html_script = '/usr/local/bin/rst2htmltypo3.py'

if mockup_uno:
    usr_bin_python = 'D:\Python27\python.exe'
    rst2html_script = 'D:\\Python27\\Scripts\\rst2htmltypo3.py'


class ContentHandlerExtensions(sax.handler.ContentHandler):

    def __init__(self, processor=None):
        sax.handler.ContentHandler.__init__(self)
        self.document = ['']
        self.extensionkey = ''
        self.version = ''
        self.process = processor

    def setProcessor(self, processor):
        self.process = processor

    def startDocument(self):
        self.document = ['']

    def startElement(self, name, attrs):
        self.document.append(name)
        if name == 'extension':
            self.extensionkey = attrs['extensionkey']
        elif name == 'version':
            self.version = attrs['version']

    def endElement(self, name):
        nameold = self.document.pop()
        if name == 'version':
            if self.process:
                self.process(self.extensionkey, self.version)

    def characters(self, content):
        pass

    def ignorableWhitespace(self, content):
        pass

    def processingInstruction(self, target, data):
        pass


def convertsxw2html(srcfile, destfile):
    error = None
    if mockup_uno:
        pass
        # file(destfile,'w').close()
    else:    
        try:
            converter.convert(srcfile, destfile)
        except dc.DocumentConversionException, exception:
            error = "ERROR1! " + str(exception)
        except dc.ErrorCodeIOException, exception:
            error = "ERROR2! " % str(exception)
        except Exception, msg:
            error = "ERROR9! " + str(msg)
    return error


def extensionProcessorDoAll(extkey, version):
    global globalCountExtensions
    globalCountExtensions += 1

    result = None
    destdir = '%s/%s/%s' % (dest_path_to_extensions, extkey, version)
    url = "%s/%s/%s/" % (url_of_extensions, extkey, version)

    if not ospe(destdir):
        os.makedirs(destdir)
    srcfile = '%s/manual.sxw' % destdir

    if ospe(srcfile):
        return result

    log.msg('new: %s/%s at: %s' % (extkey, version, url), NL)
    
    wgetsource = 'http://typo3.org/extension-manuals/%s/%s/sxw/?no_cache=1' % (extkey, version)
    cmd = '/usr/bin/wget -q --output-document=%s %s' % (srcfile.replace('/',os.sep), wgetsource)
    cmd = 'wget -q --output-document=%s %s' % (srcfile.replace('/',os.sep), wgetsource)

    retCode = subprocess.call(cmd, shell=True)
    if retCode != 0:
        result = 'wget returned error code %s when getting manual.sxw to: %s' % (retCode, url)
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result

    if not ospe(srcfile):
        result = 'no manual.sxw found after wget at: %s' % url
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result

    tested = False
    try:
        iszipfile = zipfile.is_zipfile(srcfile)
        tested = True
    except:
        pass
    if not tested:
        result = "could not test manual.sxw at: %s" % url
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result

    if not iszipfile:
        result = "manual.sxw is not a zipfile: %s" % url
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result
            
    error = ''
    try:
        zf = zipfile.ZipFile(srcfile)
        testresult = zf.testzip()
        error = None
    except IOError:
        error = 'IOError'
    except:
        error = 'Unknown Error'
    if error:
        result = "manual.sxw looks like a zipfile but the zipfile test gives an '%s' at: %s" % (error, url)
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result

    if testresult:
        result = "manual.sxw looks like a zipfile but is somehow damaged at: %s" % url
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result

    srcfile = ospj(destdir, 'manual.sxw')
    destfile = ospj(destdir, 'manual.html')
    error = convertsxw2html(srcfile, destfile)
    
    if error:
        result = '%s at: %s' % (error, url)
        log.msg(result, NL)
        f2 = file(ospj(destdir, manualIsNotAvailableFile), 'w')
        f2.write(result)
        f2.close()
        return result

    cmd = 'chmod +r ' + ospj(destdir, '*')
    subprocess.call(cmd, shell=True)

    srcfile = ospj(destdir, 'manual.html')
    destfile = ospj(destdir, 'manual-cleaned.html')
    copyclean.main(srcfile, destfile)


    # manual-cleaned.html -> manual-from-tidy.html
    # # step: Use tidy to convert from HTML-4 to XHTML
    # tidy -asxhtml -utf8 -f $EXTENSIONS/$EXTKEY/nightly/tidy-error-log.txt -o $EXTENSIONS/$EXTKEY/nightly/2-from-tidy.html $EXTENSIONS/$EXTKEY/nightly/1-cleaned.html

    srcfile = ospj(destdir, 'manual-cleaned.html')
    destfile = ospj(destdir, 'manual-from-tidy.html')
    errorfile = ospj(destdir, 'tidy-error-log.txt')
    cmd = ' '.join(['tidy', '-asxhtml', '-utf8', '-f', errorfile, '-o', destfile, srcfile])
    if os.path.exists(destfile):
        os.remove(destfile)
    returncode = subprocess.call(cmd, shell=True)
    if not ospe(destfile):
        result = 'could not create %s at %s'  % (destfile, url)
        log.msg(result, NL)
        return result

    # manual-from-tidy.html -> manual.rst
    # python ooxhtml2rst-work-in-progress.py  --treefile=$EXTENSIONS/$EXTKEY/nightly/restparser-tree.txt --logfile=$EXTENSIONS/$EXTKEY/nightly/restparser-log.txt  $EXTENSIONS/$EXTKEY/nightly/2-from-tidy.html $EXTENSIONS/$EXTKEY/nightly/manual.rst  1>&2 2>$EXTENSIONS/$EXTKEY/nightly/restparser-errors.txt

    srcfile = ospj(destdir, 'manual-from-tidy.html')
    destfile = ospj(destdir, 'manual.rst')
    treefile = f3name = ospj(destdir, 'restparser-tree.txt')
    treefile = f3name = None
    logfile = f4name = ospj(destdir, 'restparser-log.txt')
    logfile = f4name = None
    if ospe(destfile):
        os.remove(destfile)
    # ooxhtml2rst.main(f1name, f2name, f3name=None, f4name=None, appendlog=0, taginfo=0):
    ooxhtml2rst.main( srcfile, destfile, treefile, logfile)
    if not ospe(destfile):
        result = 'could not create %s at %s' % (destfile, url)
        log.msg(result, NL)
        return result


    # step: Generate single HTML file from single reST file using the Docutils (no Sphinx involved here)
    # rst2htmltypo3.py --link-stylesheet --stylesheet-path=/css/typo3_docutils_styles.css --warnings=$EXTENSIONS/$EXTKEY/nightly/rst2html-warnings.txt   $EXTENSIONS/$EXTKEY/nightly/manual.rst $EXTENSIONS/$EXTKEY/nightly/index.html

    srcfile = ospj(destdir, 'manual.rst')
    destfile = ospj(destdir, 'index.html')
    warningsfile = ospj(destdir, 'rst2html-warnings.txt')
    if os.path.exists(destfile):
        os.remove(destfile)
    cmd = ' '.join([
        usr_bin_python,
        rst2html_script,
        '--source-link',
        # '--link-stylesheet',
        # '--stylesheet-path=%s' % stylesheet_path,
        '--template=%s' % absPathToTemplate,
        '--field-name-limit=0',
        '--warnings=%s' % warningsfile,
        srcfile,
        destfile,
    ])
    devnull = file('/dev/null', 'w')
    #returncode = subprocess.call(cmd, stdout=devnull, stderr=devnull, shell=True)
    returncode = subprocess.call(cmd, shell=True)
    devnull.close()
    if not ospe(destfile):
        result = 'could not create index.html from manual.rst at %s'  % url
        log.msg(result, NL)
        return result

    return result


def extensionProcessorRst2Html(extkey, version):
    global globalCountExtensions
    globalCountExtensions += 1

    result = None
    destdir = '%s/%s/%s' % (dest_path_to_extensions, extkey, version)
    url = "%s/%s/%s/" % (url_of_extensions, extkey, version)



    # step: Generate single HTML file from single reST file using the Docutils (no Sphinx involved here)
    # rst2htmltypo3.py --link-stylesheet --stylesheet-path=/css/typo3_docutils_styles.css --warnings=$EXTENSIONS/$EXTKEY/nightly/rst2html-warnings.txt   $EXTENSIONS/$EXTKEY/nightly/manual.rst $EXTENSIONS/$EXTKEY/nightly/index.html

    srcfile = ospj(destdir, 'manual.rst')
    if not ospe(srcfile):
        result = 'no file %s/%s/manual.rst' % (extkey, version)
        log.msg(result, NL)
        return result

    destfile = ospj(destdir, 'index.html')
    warningsfile = ospj(destdir, 'rst2html-warnings.txt')
    if not simulate and os.path.exists(destfile):
        os.remove(destfile)
    cmd = ' '.join([
        usr_bin_python,
        rst2html_script,
        '--source-link',
        # '--link-stylesheet',
        # '--stylesheet-path=%s' % stylesheet_path,
        '--template=%s' % absPathToTemplate,
        '--field-name-limit=0',
        '--warnings=%s' % warningsfile,
        srcfile,
        destfile,
    ])
    cmdlog.msg('# ' + cmd, NL, dt=None)
    devnull = file('/dev/null', 'w')
    if not simulate:
        returncode = subprocess.call(cmd, stdout=devnull, stderr=devnull, shell=True)
    #returncode = subprocess.call(cmd, shell=True)
    devnull.close()

    if not ospe(destfile):
        result = 'could not create %s/%s/index.html'  % (extkey, version)
        log.msg(result, NL)
        return result
    result = 'done: %s/%s'  % (extkey, version)
    log.msg(result, NL, cnt=True)
    result = None

    return result


def getExtensionList():
    global globalIndexPageNeedsRebuild
    global globalTimeStr
    error = None
    hasChanged = False
    md5file = ospj(tempdir, 'extensions.md5')

    oldmd5 = None
    try:
        oldmd5 = file(md5file).read()
        result = 'old md5 is: %s' % oldmd5
    except:
        result = "could not read old md5 file '%s'" % md5file
    log.msg(result, NL)

    destfile = ospj(tempdir, extensions_xml_gz_fname)
    if 0 and ospe(destfile):
        pass
        # os.remove(destfile)
        subprocess.call('ls -la %s' % tempdir, shell=True)
    wget_cmd = '/usr/bin/wget -q --output-document="%s" ' % destfile
    wget_cmd = 'wget -q --output-document="%s" ' % destfile
    wget_cmd = 'wget -nv -N --output-document="%s" ' % destfile
    wget_cmd = 'wget -nv -N -P "%s" ' % tempdir
    for url in extensions_xml_gz_urls:
        temp = url.split('/')
        temp[-1] = 'extensions.md5'
        md5url = '/'.join(temp)
        if oldmd5:
            newmd5 = None
            try:
                newmd5 = urllib.urlopen(md5url).read()
            except:
                pass
        if oldmd5 and newmd5 and oldmd5==newmd5:
            result = 'md5 did not change: %s' % oldmd5
            log.msg(result, NL)
            error = None
            # return error, hasChanged

        md5file = ospj(tempdir, 'extensions.md5')
        if ospe(md5file):
            os.remove(md5file)

        oldtime = None
        try:
            oldtime = os.stat(destfile).st_mtime
        except:
            pass

        log.msg('fetch %s' % url, NL)
        cmd = '%s %s %s' % (wget_cmd, md5url, url)
        retCode = subprocess.call(cmd, shell=True)
        if retCode == 0:
            break
    else:
        error = 'abort: could not fetch file extensions.xml.gz'
        log.msg('abort: could not fetch %s' % destfile, NL)
        return error, hasChanged

    if not ospe(destfile):
        error = 'could not fetch %s' % destfile
        log.msg(error, NL)
        return error, hasChanged

    newmd5 = None
    try:
        newmd5 = file(md5file).read()
        result = 'new md5 is: %s' % newmd5
    except:
        result = "could not read new md5 file '%s'" % md5file
    log.msg(result, NL)


    newtime = None
    try:
        newtime = os.stat(destfile).st_mtime
    except:
        pass

    newtimestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(newtime))
    globalTimeStr = newtimestr
    if oldtime and newtime and oldtime == newtime:
        result = 'extensions.xml.gz %s did not change' % newtimestr
        log.msg(result, NL)
        error = None
        return error, hasChanged

    log.msg('timestamp of extensions.xml.gz is: %s' % newtimestr, NL)

    if 0:
        subprocess.call('ls -la %s' % tempdir, shell=True)

    srcfile = ospj(tempdir, extensions_xml_gz_fname)
    destfile = ospj(tempdir, extensions_xml_fname)
    log.msg('unpack %s' % srcfile, NL)
    try:
        f1 = gzip.GzipFile(srcfile)
    except:
        error = 'cannot open %s' % srcfile
        log.msg(error, NL)
        return error, hasChanged
    
    f2 = file(destfile, 'w')
    for line in f1:
        f2.write(line)
    f2.close()
    f1.close()
    
    hasChanged = True
    return error, hasChanged


def processExtensionList(theExtensionProcessor):
    global globalIndexPageNeedsRebuild
    global globalTimeStr
    error = None

    globalIndexPageNeedsRebuild = True
    log.msg('read extension list', NL)
    srcfile = ospj(tempdir, extensions_xml_fname)
    if not ospe(srcfile):
        error = 'file does not exist: %s' % extensions_xml_fname
        log.msg(error, NL)
        return error
    che = ContentHandlerExtensions()
    che.setProcessor(theExtensionProcessor)
    parser = sax.make_parser()
    parser.setContentHandler(che)
    parser.parse(srcfile)
    log.msg('%s extensions processed' % globalCountExtensions, NL)
    return error

    

if __name__ == '__main__':
   
    cmdlog = logger.Logger(ospj(tempdir,'011_cmd_log.txt'))

    log = logger.Logger()
    log.msg('Starting ...', NL)
    error, hasChanged = getExtensionList()
    if 0 and not error and hasChanged:
        error = processExtensionList(extensionProcessorDoAll)

    if not error:
        error = processExtensionList(extensionProcessorRst2Html)

    if globalIndexPageNeedsRebuild:
        log.msg('rebuild index page', NL)
        import cronjob_rebuild_index as buildindex
        buildindex.main(globalTimeStr)

    log.msg('Done.', NL)
    log.close()
    cmdlog.close()
