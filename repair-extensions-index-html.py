#! /usr/bin/python 

# mb, 2012-05-26, 2013-02-23

import os
import sys
from datetime import datetime

ospj = os.path.join

dest_path_to_extensions = '/home/mbless/public_html/typo3cms/extensions'
tempdir = '/home/mbless/HTDOCS/render-ter-extensions/temp'

oldstr = """\
<link title="Standard style" href="/css/typo3_docutils_styles.css"        type="text/css" rel="stylesheet" />
<link title="Test style 1"   href="/css/typo3_docutils_styles_test_1.css" type="text/css" rel="alternate stylesheet" />
<link title="Test style 2"   href="/css/typo3_docutils_styles_test_2.css" type="text/css" rel="alternate stylesheet" />
<link title="Test style 3"   href="/css/typo3_docutils_styles_test_3.css" type="text/css" rel="alternate stylesheet" />
""".replace('\n', '\r\n')

newstr = """\
<link                        href="/css/typo3_docutils_styles.css"          type="text/css" rel="stylesheet" />
<link title="Standard style" href="/css/typo3_docutils_styles_standard.css" type="text/css" rel="stylesheet" />
<link title="Test style 1"   href="/css/typo3_docutils_styles_test_1.css"   type="text/css" rel="alternate stylesheet" />
<link title="Test style 2"   href="/css/typo3_docutils_styles_test_2.css"   type="text/css" rel="alternate stylesheet" />
<link title="Test style 3"   href="/css/typo3_docutils_styles_test_3.css"   type="text/css" rel="alternate stylesheet" />
""".replace('\n', '\r\n')


def walk_ter_extensions_index_html(rootfolder, f2log=sys.stdout):
    fixedpart = len(os.path.join(rootfolder,'a')) - 1
    cnt = 0
    for path, dirs, files in os.walk(rootfolder):
        indexhtml = os.path.join(path, 'index.html')
        if os.path.exists(indexhtml):
            f1 = file(indexhtml)
            data = f1.read()
            f1.close()
            if oldstr in data:
                found = '1, yes found'
                f2 = file(indexhtml, 'w')
                data = data.replace(oldstr, newstr)
                f2.write(data)
                f2.close()
            else:
                found = '0, no not found'
                
            cnt += 1
            f2log.write( '%s, %s, %s,\n' % (cnt, path[fixedpart:], found))
        if cnt > 100:
            pass
            # break

def main( timestr=None):
    tempfile = ospj(tempdir, 'repair-extensions-index-html-002.txt')
    f2log = file(tempfile,'w')
    walk_ter_extensions_index_html(dest_path_to_extensions, f2log)
    f2log.close()

if __name__ == "__main__":
    main()