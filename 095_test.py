# mb, 2012-05-07, 2012-05-07

import os
import sys
import subprocess
import zipfile
import logger

ospj = os.path.join
ospe = os.path.exists

testlimit = None
NL = '\n'

# status-of-manual-sxw-files.txt
# manual-is-not-available.txt
# errorfilename = 'sxw2html-conversion-error.txt'

log = logger.Logger() 

log.msg('Starting.', NL)
log.msg("Trying to convert proper but missing manual(s).sxw.", NL, dt=False)

mockup_uno = False
cnt = 0
cntok = 0

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

def convert(srcfile, destfile):
    errormsg = None
    if mockup_uno:
        pass
        # file(destfile,'w').close()
    else:    
        try:
            converter.convert(srcfile, destfile)
        except dc.DocumentConversionException, exception:
            errormsg = "ERROR1! " + str(exception)
        except dc.ErrorCodeIOException, exception:
            errormsg = "ERROR2! " % str(exception)
        except Exception, msg:
            errormsg = "ERROR9! " + str(msg)
    return errormsg

    
def traverse_tree(startfolder):
    cnt = 0
    breaking = False
    for destdir, dirs, files in os.walk(startfolder):
        if cnt and cnt >= testlimit:
            breaking = True
        if breaking:
            dirs[:] = []
            break
        dirs.sort()
        left, version = os.path.split(destdir)
        left, extkey = os.path.split(left)
        displayname = ospj(extkey, version)
        proceed = True
        leaf = os.path.split(destdir)[1]
        if not (leaf == "nightly" or len(leaf.split('.')) == 3):
            proceed = False
            continue
        # log.msg(displayname, NL, dt=False)
        srcfile = ospj(destdir, 'manual.sxw')
        if not ospe(srcfile):
            proceed = False
            continue
        destfile = ospj(destdir, 'manual.html')
        if ospe(destfile):
            proceed = False
            log.msg('%-10s , %s' % ('ok exists', displayname), NL)
            continue
        manualisnotavailablefile = ospj(destdir, 'manual-is-not-available.txt')
        sxw2htmlconversionerrorfile = 'sxw2html-conversion-error.txt'
        for afile in [manualisnotavailablefile, sxw2htmlconversionerrorfile]:
            if ospe(afile):
                os.remove(afile)
        if proceed:
            tested = False
            try:
                iszipfile = zipfile.is_zipfile(srcfile)
                tested = True
            except:
                pass
            if not tested:
                log.msg('%-10s , %s' % ('could not test', displayname), NL)
                f2 = file(manualisnotavailablefile,'w')
                f2.write('could not test manual.sxw for being a zipfile\n')
                f2.close()
                proceed = False
               
        if proceed:
            error = ''
            try:
                zf = zipfile.ZipFile(srcfile)
                testresult = zf.testzip()
                error = None
            except IOError:
                error = 'IOError'
            except:
                error = 'Error'
            if not (error is None and testresult is None):
                log.msg('%-10s , %s' % ('no zipfile', displayname), NL)
                f2 = file(manualisnotavailablefile,'w')
                f2.write('manual.sxw is not a proper zipfile\n')
                f2.close()
                proceed = False

        if proceed:
            error = convert(srcfile, destfile)
            if error is None:
                result1 = 'ok'
            else:
                result1 = str(error)
            if os.path.exists(destfile):
                result2 = 'ok'
            else:
                result2 = 'not created'
            if result2 == 'ok':
                log.msg('%-10s , %s' % ('%s;%s' % (result1, result2), displayname), NL, cnt=True)
                cnt += 1
            else:
                log.msg('%-10s , %s' % ('%s;%s' % (result1, result2), displayname), NL, cnt=True)

if __name__=="__main__":
    traverse_tree(dest_path_to_extensions)


log.msg('Done.', NL)

