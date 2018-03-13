
import os
import sys
import subprocess
import copyclean
import ooxhtml2rst_work_in_progress as ooxhtml2rst

dest_path_to_extensions = '/home/mbless/public_html/typo3/extensions'
errorfilename = 'sxw2html-conversion-error.txt'
stylesheet_path = 'https://docs.typo3.org/css/typo3_docutils_styles.css'
proceeding = True

usr_bin_python = '/usr/bin/python'
rst2html_script = '/usr/local/bin/rst2htmltypo3.py'

if 0 and 'Local testing on windows':
    usr_bin_python = 'D:\Python27\python.exe'
    dest_path_to_extensions = r'D:\TYPO3-Documentation\t3doc-srv123-mbless\public_html\typo3\extensions' '\\'
    rst2html_script = 'D:\\Python27\\Scripts\\rst2htmltypo3.py'


def walk_ter_manuals_html_to_rest(rootfolder):
    prelpath = len(rootfolder)
    proceeding = True
    cnt = 0
    cntnew = 0

    for path, dirs, files in os.walk(rootfolder):
        proceedwithfile = True
        destdir = path
        dirs.sort()
        if not proceeding:
            dirs[:] = []
            break
        else:
            for afile in files:
                if not proceeding:
                    break
                if afile == 'manual.html' and len(os.path.split(path)[1].split('.')) == 3:
                    left, version = os.path.split(path)
                    left, extkey = os.path.split(left)
                    manualhtmlfile = os.path.join(path, 'manual.html')
                    manualhtmlfile = os.path.join(path, afile)
                    cleanedfile = os.path.join(destdir, 'manual-cleaned.html')
                    tidyfile = os.path.join(destdir, 'manual-from-tidy.html')
                    rstfile = os.path.join(destdir, 'manual.rst')
                    indexhtmlfile = os.path.join(destdir, 'index.html')
                    finaldestfile = indexhtmlfile

                    cnt += 1
                    if 0 and 'force rebuild':
                        if os.path.exists(indexhtmlfile):
                            os.remove(indexhtmlfile)

                    if 1:
                        cmd = 'chmod +r ' + os.path.join(destdir, '*')
                        subprocess.call(cmd, shell=True)

                    if proceedwithfile and os.path.exists(finaldestfile):
                        # nothing to do?
                        print '%04d %4d exists: %s' % (cnt, cntnew, finaldestfile[prelpath:])
                        proceedwithfile = False

                    if proceedwithfile:
                        # manual.html -> manual-cleaned.html
                        srcfile = manualhtmlfile
                        destfile = cleanedfile
                        print '%04d %4d new: %s' % (cnt, cntnew, srcfile[prelpath:])
                        print srcfile
                        if os.path.exists(destfile):
                            os.remove(destfile)
                        proceedwithfile = not os.path.exists(destfile)
                        if not proceedwithfile:
                            print 'could not remove %s'  % destfile
                        if proceedwithfile:
                            copyclean.main(srcfile, destfile)
                            proceedwithfile = os.path.exists(cleanedfile)
                        if not proceedwithfile:
                            print 'could not create %s' % destfile

                    if proceedwithfile:
                        # manual-cleaned.html -> manual-from-tidy.html
                        # # step: Use tidy to convert from HTML-4 to XHTML
                        # tidy -asxhtml -utf8 -f $EXTENSIONS/$EXTKEY/nightly/tidy-error-log.txt -o $EXTENSIONS/$EXTKEY/nightly/2-from-tidy.html $EXTENSIONS/$EXTKEY/nightly/1-cleaned.html

                        srdfile = cleanedfile
                        destfile = tidyfile
                        errorfile = os.path.join(destdir, 'tidy-error-log.txt')
                        cmd = ' '.join(['tidy', '-asxhtml', '-utf8', '-f', errorfile, '-o', destfile, cleanedfile])
                        if os.path.exists(destfile):
                            os.remove(destfile)
                        proceedwithfile = not os.path.exists(destfile)
                        if not proceedwithfile:
                            print 'could not remove %s'  % destfile
                        if proceedwithfile:
                            returncode = subprocess.call(cmd, shell=True)
                        proceedwithfile = os.path.exists(destfile)
                        if not proceedwithfile:
                            print 'could not create %s'  % destfile

                    if proceedwithfile:
                        # manual-from-tidy.html -> manual.rst
                        # python ooxhtml2rst-work-in-progress.py  --treefile=$EXTENSIONS/$EXTKEY/nightly/restparser-tree.txt --logfile=$EXTENSIONS/$EXTKEY/nightly/restparser-log.txt  $EXTENSIONS/$EXTKEY/nightly/2-from-tidy.html $EXTENSIONS/$EXTKEY/nightly/manual.rst  1>&2 2>$EXTENSIONS/$EXTKEY/nightly/restparser-errors.txt

                        srcfile = tidyfile
                        destfile = rstfile
                        # treefile = f3name = 'restparser-tree.txt'
                        treefile = f3name = None
                        # logfile = f4name = os.path.join(destdir, 'restparser-log.txt')
                        logfile = f4name = None
                        if os.path.exists(destfile):
                            os.remove(destfile)
                        proceedwithfile = not os.path.exists(destfile)
                        if not proceedwithfile:
                            print 'could not remove %s'  % destfile
                        if proceedwithfile:
                            # ooxhtml2rst.main(f1name, f2name, f3name=None, f4name=None, appendlog=0, taginfo=0):
                            ooxhtml2rst.main( srcfile, destfile, treefile, logfile)
                            proceedwithfile = os.path.exists(destfile)
                        if not proceedwithfile:
                            print 'could not create %s'  % (destfile, )


                    if proceedwithfile:
                        # step: Generate single HTML file from single reST file using the Docutils (no Sphinx involved here)
                        # rst2htmltypo3.py --link-stylesheet --stylesheet-path=/css/typo3_docutils_styles.css --warnings=$EXTENSIONS/$EXTKEY/nightly/rst2html-warnings.txt   $EXTENSIONS/$EXTKEY/nightly/manual.rst $EXTENSIONS/$EXTKEY/nightly/index.html

                        srcfile = os.path.join(destdir, 'manual.rst')
                        destfile = os.path.join(destdir, 'index.html')

                    if proceedwithfile:
                        # manual.rst -> index.html

                        srcfile = rstfile
                        destfile = indexhtmlfile
                        warningsfile = os.path.join(destdir, 'rst2html-warnings.txt')

                        if os.path.exists(destfile):
                            os.remove(destfile)
                        proceedwithfile = not os.path.exists(destfile)
                        if not proceedwithfile:
                            print 'could not remove %s'  % destfile
                        if proceedwithfile:
                            cmd = ' '.join([
                                usr_bin_python,
                                rst2html_script,
                                '--source-link',
                                '--link-stylesheet',
                                '--stylesheet-path=%s' % stylesheet_path,
                                '--field-name-limit=0',
                                '--warnings=%s' % warningsfile,
                                srcfile,
                                destfile,
                            ])
                            
                            returncode = subprocess.call(cmd, shell=True)
                            proceedwithfile = os.path.exists(destfile)

                        if not proceedwithfile:
                            print 'could not create %s'  % (destfile, )
                        else:
                            cntnew += 1


                    if 0 and cntnew > 100:
                        proceeding = False
                        break
    print
    return proceeding



if __name__ == "__main__":
    walk_ter_manuals_html_to_rest(dest_path_to_extensions)
