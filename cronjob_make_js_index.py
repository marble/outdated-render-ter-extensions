#! /usr/bin/python

# cronjob_make_js_index.py, mb, 2012-05-26, 2013-02-24

import os
import sys
import shutil
import json
from datetime import datetime

ospj = os.path.join

dest_path_to_extensions = '/home/mbless/public_html/TYPO3/extensions'
tempdir = '/home/mbless/HTDOCS/render-ter-extensions/temp'

document_part_1 = """\
var extensionList = [
"""

document_part_2 = """\
];
"""

def example():
    extensionList = [
        { "key" : "a1_teasermenu",
          "latest":"0.1.0",
          "versions" : ["0.1.0"]
          }
        ]

def main( timestr=None):
    cntlines = 0
    extkey0 = None
    extensionsList = []
    f1name = ospj(tempdir, 'tempfile-ter-manuals-2.txt')
    f1 = file(f1name)
    f2 = file(ospj(tempdir, 'tempfile-ter-manuals-4.js'), 'w')

    if (1):
        if timestr is None:
            str(datetime.now())[:19]
        # a bit of information at the top ...
        f2.write('// generated: %s\n' % timestr)
        f2.write('// from     : %s\n' % f1name)

    f2.write(document_part_1)
    for line in f1:
        cntlines += 1
        extkey, dummy, version = line.strip().split(',')
        if extkey != extkey0:
            extension = {'key':extkey, 'latest': version, 'versions': [version]}
            extensionsList.append(extension)
        else:
            extension['latest'] = version
            extension['versions'].insert(0, version)
        extkey0 = extkey

    for ext in extensionsList:
        versions = repr(ext['versions']).replace(' ','')
        f2.write('\t{"key":%r,"latest":%r,"versions":%s},\n' % (ext['key'], ext['latest'], versions))

    f2.write(document_part_2)
    f2.close()
    f1.close()

    if 0:
        srcfile = ospj(tempdir, 'tempfile-extensions.json')
        destfile = os.path.join(dest_path_to_extensions, 'index.html')
        shutil.copyfile(srcfile, destfile)

if __name__ == "__main__":
    main()
