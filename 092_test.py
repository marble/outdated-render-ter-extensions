import os
import sys
import subprocess
#import documentconverter as dc
import zipfile
import logger

NL = '\n'
# status-of-manual-sxw-files.txt
log = logger.Logger() 

log.msg('Starting.', NL)
log.msg("Checking the 'manual.sxw' files.", NL, dt=False)

cnt = 0
cntok = 0
dest_path_to_extensions = '/home/mbless/public_html/typo3/extensions'
if not os.path.isdir(dest_path_to_extensions):
    dest_path_to_extensions = r'U:\htdocs\LinuxData200\srv123-typo3-org\remote\public_html\typo3\extensions'
if not os.path.isdir(dest_path_to_extensions):
    dest_path_to_extensions = ''
if not os.path.isdir(dest_path_to_extensions):
    log.msg("abort: Don't know the path to the extensions.", NL)
    sys.exit(2)
    

errorfilename = 'sxw2html-conversion-error.txt'

if 0 and 'remove lockfiles':
    log.msg("looking for '.~lock.manual.sxw#' lockfiles", NL)
    cmd = 'find %s -type f -name ".~lock.manual.sxw#"' % dest_path_to_extensions
    log.msg('cmd: %s' % cmd, NL)
    subprocess.call(cmd, stdout=log.stream(), shell=True)

    log.msg("remove '.~lock.manual.sxw#' lockfiles", NL)
    cmd = 'find %s -type f -name ".~lock.manual.sxw#" -exec rm {} ";"' % dest_path_to_extensions
    log.msg('cmd: %s' % cmd, NL)
    subprocess.call(cmd, stdout=log.stream(), shell=True)

    log.msg("after removing:", NL)
    log.msg("looking for '.~lock.manual.sxw#' lockfiles", NL)
    cmd = 'find %s -type f -name ".~lock.manual.sxw#"' % dest_path_to_extensions
    log.msg('cmd: %s' % cmd, NL)
    subprocess.call(cmd, stdout=log.stream(), shell=True)

#converter = dc.DocumentConverter()    

breaking = False
for destdir, dirs, files in os.walk(dest_path_to_extensions):
    if breaking:
        dirs[:] = []
        break
    dirs.sort()
    left, version = os.path.split(destdir)
    left, extkey = os.path.split(left)
    displayname = os.path.join(extkey, version)
    proceed = True

    afile = 'manual.sxw'
    leaf = os.path.split(destdir)[1]
    if not (leaf == "nightly" or len(leaf.split('.')) == 3):
        proceed = False

    if proceed and not afile in files:
        log.msg('%-10s , %s' % ('no file', displayname), NL,  dt=False)
        proceed = False
    
    if proceed and len(os.path.split(destdir)[1].split('.')) == 3:
        srcfile = os.path.join(destdir, afile)

        if proceed:
            tested = False
            try:
                iszipfile = zipfile.is_zipfile(srcfile)
                tested = True
            except:
                pass
            if not tested:
                log.msg('%-10s , %s' % ('could not test', displayname), NL, dt=False)
                proceed = False
            elif not iszipfile:
                log.msg('%-10s , %s' % ('no zipfile', displayname), NL, dt=False)
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
            if error is None:
                if testresult is None:
                    msg = 'ok'
                else:
                    msg = 'corrupted'
            else:
                msg = error
            log.msg('%-10s , %s' % (msg,displayname), NL, dt=False)
            proceed = False
        
            log.msg('%-10s , %s' % (msg,displayname), NL, dt=False)

log.msg('Done.', NL)
