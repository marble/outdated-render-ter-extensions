# cronjob_finally_publish, mb, 2012-05-26, 2013-02-22

import os
import sys
import subprocess
import shutil
from datetime import datetime

ospj = os.path.join

dest_path_to_extensions = '/home/mbless/public_html/typo3cms/extensions'
tempdir = '/home/mbless/HTDOCS/render-ter-extensions/temp'

def main( timestr=None):

    srcfile = ospj(tempdir, 'tempfile-ter-manuals-3-index.html')
    destfile = os.path.join(dest_path_to_extensions, 'index2.html')
    shutil.copyfile(srcfile, destfile)

    srcfile = ospj(tempdir, 'tempfile-ter-manuals-4.js')
    destfile = os.path.join(dest_path_to_extensions, 'extensions.js')
    shutil.copyfile(srcfile, destfile)

if __name__ == "__main__":
    main()