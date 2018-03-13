# mb, 2012-05-26, 2013-02-28

import os
import sys
import subprocess
import shutil
from datetime import datetime

ospj = os.path.join

dest_path_to_extensions = '/home/mbless/public_html/TYPO3/extensions'
tempdir = '/home/mbless/HTDOCS/render-ter-extensions/temp'

proceeding = True

stats = {}

def walk_ter_extensions_index_html(rootfolder, f2=sys.stdout):
    prelpath = len(rootfolder)
    proceeding = True

    for path, dirs, files in os.walk(rootfolder):
        proceedwithfile = True
        destdir = path
        if not proceeding:
            dirs[:] = []
        else:
            if os.path.exists(os.path.join(path, 'manual-is-not-available.txt')):
                stats['manual-is-not-available.txt'] = stats.get('manual-is-not-available.txt', 0) + 1
            else:
                for afile in ['index.html', 'manual.sxw', 'manual.html', 'manual.rst']:
                    if os.path.exists(os.path.join(path, afile)):
                        stats[afile] = stats.get(afile, 0) + 1

            for afile in files:

                leaf = os.path.split(path)[1]
                vsplitted = leaf.split('.')
                if afile.lower() == 'index.html' and (leaf=='latest' or len(vsplitted) == 3):
                    if leaf == 'latest':
                        vsplitted = ['999','999','999']
                    try:
                        vsplitted = [int(v) for v in vsplitted]
                        skip = False
                    except ValueError:
                        skip = True
                    if skip:
                        continue
                    left, version = os.path.split(path)
                    left, extkey = os.path.split(left)
                    v1, v2, v3 = vsplitted
                    f2.write(extkey + ',%05d.'%v1 + '%05d.'%v2 + '%05d'%v3 + ',' + version + '\n')



document_part_1 = """\
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Extensions</title>
<link rel="stylesheet" href="https://docs.typo3.org/css/typo3_docutils_styles.css" type="text/css" />
</head>
<body>
<div class="document">
"""

document_part_2 = """\
</div>
</body>
</html>
"""

def main( timestr=None):
    tempfile = ospj(tempdir, 'tempfile-ter-manuals-1.txt')
    f2 = file(tempfile,'w')
    walk_ter_extensions_index_html(dest_path_to_extensions, f2)
    f2.close()

    f1 = file(ospj(tempdir, 'tempfile-ter-manuals-1.txt'))
    f2 = file(ospj(tempdir, 'tempfile-ter-manuals-2.txt'), 'w')
    subprocess.call('sort', stdin=f1, stdout=f2)
    f1.close()
    f2.close()

    extkey0 = None
    version0 = None
    firstletter0 = None
    firstletter00 = ''

    cntlines = 0
    cntlinks = 0
    f1 = file(ospj(tempdir, 'tempfile-ter-manuals-2.txt'))
    f2 = file(ospj(tempdir, 'tempfile-ter-manuals-3-index.html'), 'w')
    f2.write(document_part_1)

    if timestr is None:
        timestr =  str(datetime.now())[:19]
        f2.write('<pre>')
        f2.write(timestr)
        f2.write("       updated every 2 hours at HH:10\n")
        f2.write('</pre>\n')
    else:
        f2.write('<pre>')
        f2.write("This list reflects extensions.xml.gz %s\n" % timestr)
        f2.write("Updated every 2 hours at HH:10\n")
        f2.write('</pre>\n')

    #f2.write('<p>'
    #    'The links will open in a second window. I you arrange the two windows '
    #    'side by side you can click an extension in this window and '
    #    'immediately read in the other.</p>'
    #)
    if timestr < '2012-12-30 16:00:00':
        f2.write('<p><b>'
            "Due to the way TER works it may take "
            'up to a day until new manuals appear.'
            '</b></p>'
        )
    if timestr < '2011-12-30 16:00:00':
        f2.write('<p><b>'
            "http://typo3.org doesn\'t hand out new 'manual.sxw' files at the moment. "
            'So we are not getting any updates at the moment. This will be repaired '
            'once typo3.org works again. ~Martin,&nbsp;2012-05-21&nbsp;18:35'
            '</b></p>'
        )
    for line in f1:
        cntlines += 1
        extkey, dummy, version = line.strip().split(',')
        firstletter = extkey[0]
        if not extkey0 is None:
            if firstletter0 != firstletter00:
                f2.write('<br /><br /><b>%s</b><br />\n' % firstletter0)
                firstletter00 = firstletter0
            if extkey != extkey0:
                f2.write('<a href="%s/%s/" title="%s %s" >%s</a><br />\n' % (extkey0, version0, extkey0, version0, extkey0))
                cntlinks += 1
        firstletter0 = firstletter
        extkey0 = extkey
        version0 = version
    if not extkey0 is None:
        if firstletter0 != firstletter00:
            f2.write('<br /><br /><b>%s</b><br />\n' % firstletter0)
            firstletter00 = firstletter0
        f2.write('<a href="%s/%s/" title="%s %s" >%s</a>\n' % (extkey0, version0, extkey0, version0, extkey0))

    f2.write('<pre>\n')
    f2.write('%s\n\n' % (str(datetime.now())[:19]))
    f2.write('Available:\n')
    f2.write('\n')
    f2.write('%6d links on this page to different extensions.\n' % cntlinks)
    f2.write('       The links point to the latest version which has an index.html\n')
    f2.write('\n')
    f2.write('%6d with manual.sxw  (made by extension author)\n' % stats['manual.sxw'])
    f2.write('%6d with manual.html (made from manual.sxw)\n'     % stats['manual.html'])
    f2.write('%6d with manual.rst  (made from manual.html)\n'    % stats['manual.rst'])
    f2.write('%6d with index.html  (made from manual.rst)\n'     % stats['index.html'])
    f2.write('\n')
    f2.write("%6d don't have a manual at http://typo3.org/extension-manuals/EXTKEY/VERSION/sxw/?no_cache=1\n" % stats['manual-is-not-available.txt'])
    f2.write('</pre>')

    f2.write(document_part_2)
    f2.close()

    if (0):
        # moved this functionality to the caller to make everything more "atomic"
        srcfile = ospj(tempdir, 'tempfile-ter-manuals-3-index.html')
        destfile = os.path.join(dest_path_to_extensions, 'index.html')
        shutil.copyfile(srcfile, destfile)

if __name__ == "__main__":
    main()