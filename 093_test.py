import os
import sys
import subprocess
import zipfile
import logger


f1name = 'status-of-manual-sxw-files.txt'
destdir = './temp'
testlimit = None
NL = '\n'
# status-of-manual-sxw-files.txt
log = logger.Logger() 

log.msg('Starting.', NL)
log.msg("Try to convert 'ok' manuals only.", NL, dt=False)

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
    
if not os.path.isdir(destdir):
    os.makedirs(destdir)
if not os.path.isdir(destdir):
    log.msg("abort: cannot create '%s'" % destdir, NL)
    sys.exit(2)


if not mockup_uno:
    import documentconverter as dc
    
    converter = dc.DocumentConverter()    


def convert(srcfile, destfile):
    errormsg = None

    if mockup_uno:
        file(destfile,'w').close()
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

skipping = True

f1 = file(f1name)
for lineno, line in enumerate(f1):
    if testlimit and lineno >= testlimit:
        break
    
    parts = line.split(',')
    if len(parts) == 2:
        status, extension = parts
        status = status.strip()
        extension = extension.strip()
        if skipping:
            if extension == 'mwimagemap/1.0.0':
                skipping = False
            else:
                continue
        if status == 'ok':
            srcfile = os.path.join(dest_path_to_extensions, extension, 'manual.sxw')
            destfile = os.path.join(destdir,'manual.html')
            if os.listdir(os.path.join(destdir)):
                subprocess.call('rm ' + os.path.join(destdir,'*'), shell=True)
            if os.listdir(os.path.join(destdir)):
                log.msg("abort: cannot empty '%s'" % destdir, NL)
                sys.exit(2)
            if 0:
                print srcfile
                print destfile

            error = convert(srcfile, destfile)
            if error is None:
                result1 = 'ok'
            else:
                result1 = str(error)

            if os.path.exists(destfile):
                result2 = 'ok'
            else:
                result2 = 'not created'
            log.msg('%-10s , %s' % ('%s;%s' % (result1, result2), extension), NL, cnt=True)

f1.close()
    
log.msg('Done.', NL)
