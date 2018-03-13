#
# PyODConverter (Python OpenDocument Converter) v1.2 - 2012-03-10
#
# This script converts a document from one office format to another by
# connecting to an OpenOffice.org instance via Python-UNO bridge.
#
# Copyright (C) 2008-2012 Mirko Nasato
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl-2.1.html
# - or any later version.
#
DEFAULT_OPENOFFICE_PORT = 8100

import uno
from os.path import abspath, isfile, splitext
from com.sun.star.beans import PropertyValue
from com.sun.star.task import ErrorCodeIOException
from com.sun.star.connection import NoConnectException

FAMILY_TEXT = "Text"
FAMILY_WEB = "Web"
FAMILY_SPREADSHEET = "Spreadsheet"
FAMILY_PRESENTATION = "Presentation"
FAMILY_DRAWING = "Drawing"

#---------------------#
# Configuration Start #
#---------------------#

# see http://wiki.services.openoffice.org/wiki/Framework/Article/Filter

# most formats are auto-detected; only those requiring options are defined here
IMPORT_FILTER_MAP = {
    "txt": {
        "FilterName": "Text (encoded)",
        "FilterOptions": "utf8"
    },
    "csv": {
        "FilterName": "Text - txt - csv (StarCalc)",
        "FilterOptions": "44,34,0"
    }
}

EXPORT_FILTER_MAP = {
    "pdf": {
        FAMILY_TEXT: { "FilterName": "writer_pdf_Export" },
        FAMILY_WEB: { "FilterName": "writer_web_pdf_Export" },
        FAMILY_SPREADSHEET: { "FilterName": "calc_pdf_Export" },
        FAMILY_PRESENTATION: { "FilterName": "impress_pdf_Export" },
        FAMILY_DRAWING: { "FilterName": "draw_pdf_Export" }
    },
    "html": {
        FAMILY_TEXT: { "FilterName": "HTML (StarWriter)" },
        FAMILY_SPREADSHEET: { "FilterName": "HTML (StarCalc)" },
        FAMILY_PRESENTATION: { "FilterName": "impress_html_Export" }
    },
    "odt": {
        FAMILY_TEXT: { "FilterName": "writer8" },
        FAMILY_WEB: { "FilterName": "writerweb8_writer" }
    },
    "doc": {
        FAMILY_TEXT: { "FilterName": "MS Word 97" }
    },
    "rtf": {
        FAMILY_TEXT: { "FilterName": "Rich Text Format" }
    },
    "txt": {
        FAMILY_TEXT: {
            "FilterName": "Text",
            "FilterOptions": "utf8"
        }
    },
    "ods": {
        FAMILY_SPREADSHEET: { "FilterName": "calc8" }
    },
    "xls": {
        FAMILY_SPREADSHEET: { "FilterName": "MS Excel 97" }
    },
    "csv": {
        FAMILY_SPREADSHEET: {
            "FilterName": "Text - txt - csv (StarCalc)",
            "FilterOptions": "44,34,0"
        }
    },
    "odp": {
        FAMILY_PRESENTATION: { "FilterName": "impress8" }
    },
    "ppt": {
        FAMILY_PRESENTATION: { "FilterName": "MS PowerPoint 97" }
    },
    "swf": {
        FAMILY_DRAWING: { "FilterName": "draw_flash_Export" },
        FAMILY_PRESENTATION: { "FilterName": "impress_flash_Export" }
    }
}

PAGE_STYLE_OVERRIDE_PROPERTIES = {
    FAMILY_SPREADSHEET: {
        #--- Scale options: uncomment 1 of the 3 ---
        # a) 'Reduce / enlarge printout': 'Scaling factor'
        "PageScale": 100,
        # b) 'Fit print range(s) to width / height': 'Width in pages' and 'Height in pages'
        #"ScaleToPagesX": 1, "ScaleToPagesY": 1000,
        # c) 'Fit print range(s) on number of pages': 'Fit print range(s) on number of pages'
        #"ScaleToPages": 1,
        "PrintGrid": False
    }
}

#-------------------#
# Configuration End #
#-------------------#

class DocumentConversionException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class DocumentConverter:
    
    def __init__(self, port=DEFAULT_OPENOFFICE_PORT):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
        try:
            context = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % port)
        except NoConnectException:
            raise DocumentConversionException, "failed to connect to OpenOffice.org on port %s" % port
        self.desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)

    def convert(self, inputFile, outputFile):

        inputUrl = self._toFileUrl(inputFile)
        outputUrl = self._toFileUrl(outputFile)

        loadProperties = { "Hidden": True }
        inputExt = self._getFileExt(inputFile)
        if IMPORT_FILTER_MAP.has_key(inputExt):
            loadProperties.update(IMPORT_FILTER_MAP[inputExt])
        
        document = self.desktop.loadComponentFromURL(inputUrl, "_blank", 0, self._toProperties(loadProperties))
        try:
            document.refresh()
        except AttributeError:
            pass

        family = self._detectFamily(document)
        self._overridePageStyleProperties(document, family)
        
        outputExt = self._getFileExt(outputFile)
        storeProperties = self._getStoreProperties(document, outputExt)

        try:
            document.storeToURL(outputUrl, self._toProperties(storeProperties))
        finally:
            document.close(True)

    def _overridePageStyleProperties(self, document, family):
        if PAGE_STYLE_OVERRIDE_PROPERTIES.has_key(family):
            properties = PAGE_STYLE_OVERRIDE_PROPERTIES[family]
            pageStyles = document.getStyleFamilies().getByName('PageStyles')
            for styleName in pageStyles.getElementNames():
                pageStyle = pageStyles.getByName(styleName)
                for name, value in properties.items():
                    pageStyle.setPropertyValue(name, value)

    def _getStoreProperties(self, document, outputExt):
        family = self._detectFamily(document)
        try:
            propertiesByFamily = EXPORT_FILTER_MAP[outputExt]
        except KeyError:
            raise DocumentConversionException, "unknown output format: '%s'" % outputExt
        try:
            return propertiesByFamily[family]
        except KeyError:
            raise DocumentConversionException, "unsupported conversion: from '%s' to '%s'" % (family, outputExt)
    
    def _detectFamily(self, document):
        if document.supportsService("com.sun.star.text.WebDocument"):
            return FAMILY_WEB
        if document.supportsService("com.sun.star.text.GenericTextDocument"):
            # must be TextDocument or GlobalDocument
            return FAMILY_TEXT
        if document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
            return FAMILY_SPREADSHEET
        if document.supportsService("com.sun.star.presentation.PresentationDocument"):
            return FAMILY_PRESENTATION
        if document.supportsService("com.sun.star.drawing.DrawingDocument"):
            return FAMILY_DRAWING
        raise DocumentConversionException, "unknown document family: %s" % document

    def _getFileExt(self, path):
        ext = splitext(path)[1]
        if ext is not None:
            return ext[1:].lower()

    def _toFileUrl(self, path):
        return uno.systemPathToFileUrl(abspath(path))

    def _toProperties(self, dict):
        props = []
        for key in dict:
            prop = PropertyValue()
            prop.Name = key
            prop.Value = dict[key]
            props.append(prop)
        return tuple(props)


if 0 and __name__ == "__main__":
    from sys import argv, exit
    
    if len(argv) < 3:
        print "USAGE: python %s <input-file> <output-file>" % argv[0]
        exit(255)
    if not isfile(argv[1]):
        print "no such input file: %s" % argv[1]
        exit(1)

    try:
        converter = DocumentConverter()    
        converter.convert(argv[1], argv[2])
    except DocumentConversionException, exception:
        print "ERROR! " + str(exception)
        exit(1)
    except ErrorCodeIOException, exception:
        print "ERROR! ErrorCodeIOException %d" % exception.ErrCode
        exit(1)

if __name__ == "__main__":
    import os
    import sys
    import subprocess

    cnt = 0
    cntok = 0
    dest_path_to_extensions = '/home/mbless/public_html/typo3/extensions'
    errorfilename = 'sxw2html-conversion-error.txt'

    if 1 and 'remove lockfiles':
        print 'initially:'
        cmd = 'find %s -type f -name ".~lock.manual.sxw#"' % dest_path_to_extensions
        subprocess.call(cmd, stdout=sys.stdout, shell=True)

        print 'removing:'
        cmd = 'find %s -type f -name ".~lock.manual.sxw#" -exec rm {} ";"' % dest_path_to_extensions
        subprocess.call(cmd, stdout=sys.stdout, shell=True)

        print 'after removing:'
        cmd = 'find %s -type f -name ".~lock.manual.sxw#"' % dest_path_to_extensions
        subprocess.call(cmd, stdout=sys.stdout, shell=True)

    converter = DocumentConverter()    

    proceeding = True
    for path, dirs, files in os.walk(dest_path_to_extensions):
        dirs.sort()
        if not proceeding:
            dirs[:] = []
        else:
            for afile in files:
                if afile == 'manual.sxw' and len(os.path.split(path)[1].split('.')) == 3:
                    left, version = os.path.split(path)
                    left, extkey = os.path.split(left)
                    srcfile = os.path.join(path, afile)
                    destfile = srcfile[:-4] + '.html'
                    destdir = path
                    errorfile = os.path.join(destdir, errorfilename)
                    notavailablefile = os.path.join(destdir, 'manual-is-not-available.txt')
                    problemwithmanualsxwfile = os.path.join(destdir, 'problem-with-manual-sxw.txt')
                    cnt += 1
                    cmd = 'chmod +r ' + os.path.join(destdir, '*')
                    subprocess.call(cmd, shell=True)
                    if os.path.exists(destfile):
                        if 0:
                            print '%04d,%4d %s/%s: exists' % (cnt, cntok, extkey, version)
                    elif os.path.exists(notavailablefile):
                        if 0:
                            print '%04d,%4d no manual: %s/%s: ' % (cnt, cntok, extkey, version)
                    elif 0 and os.path.exists(errorfile):
                        if 0:
                            print '%04d,%4d %s/%s: errorfile exists' % (cnt, cntok, extkey, version)
                    else:
                        success = False
                        try:
                            pass
                            print '%04d,%4d %s/%s' % (cnt, cntok, extkey, version)
                            print srcfile
                            print destfile
                            if 0 and 'despair':
                                pidfile = '/var/run/openoffice-server.pid'
                                if os.path.exists(pidfile):
                                    subprocess.call('sudo /etc/init.d/openoffice.sh stop', shell=True)
                                if not os.path.exists(pidfile):
                                    subprocess.call('sudo /etc/init.d/openoffice.sh start', shell=True)
                                converter = DocumentConverter()    
                            converter.convert(srcfile, destfile)
                            success = True
                            cntok += 1
                        except DocumentConversionException, exception:
                            errormsg = "ERROR! " + str(exception)
                        except ErrorCodeIOException, exception:
                            errormsg = "ERROR! ErrorCodeIOException %d" % exception.ErrCode
                        except Exception, msg:
                            errormsg = "ERROR!! " + str(msg)
                        if success:
                            cmd = 'chmod +r ' + os.path.join(destdir, '*')
                            subprocess.call(cmd, shell=True)
                            if os.path.exists(errorfile):
                                try:
                                    os.remove(errorfile)
                                except:
                                    pass
                            if os.path.exists(problemwithmanualsxwfile):
                                try:
                                    os.remove(problemwithmanualsxwfile)
                                except:
                                    pass
                        if not success:
                            print errormsg
                            f2 = file(errorfile, 'w')
                            f2.write('%s\n' % errormsg)
                            f2.close()
                            if errormsg == "ERROR! unsupported conversion: from 'Web' to 'html'":
                                file(notavailablefile,'w').close()
                            else:
                                file(problemwithmanualsxwfile, 'w').close()


                if 0 and cnt > 499:
                    proceeding = False
                    break
    print

