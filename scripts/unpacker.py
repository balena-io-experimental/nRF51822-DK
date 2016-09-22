#!/usr/bin/env python

import os
import zipfile
import tempfile
import random
import string

from os.path  import basename

class Unpacker(object):
    def unpack(self, zipfile):
        if not os.path.isfile(zipfile):
            raise Exception("Error: Zip file not found")

        self.zipDir = "{0}/{1}_{2}".format(tempfile.gettempdir(),
            os.path.splitext(basename(zipfile))[0],
            self.entropy(6))

        if self.unzip(zipfile, self.zipDir) == False:
            raise Exception("Error: Unzip failed")

        datfile = ""
        binfile = ""
        for fname in os.listdir(self.zipDir):
            if fname.endswith('.dat'):
                datfile = "{0}/{1}".format(self.zipDir, fname)
                continue
            elif fname.endswith('.bin'):
                binfile = "{0}/{1}".format(self.zipDir, fname)
                continue


        if not os.path.isfile(datfile):
            raise Exception("Error: No DAT file found")
        elif not os.path.isfile(binfile):
            raise Exception("Error:No BIN file found")

        return binfile, datfile

    def unzip(self, zipSrc, zipDir):
        try:
           zip = zipfile.ZipFile(r'{0}'.format(zipSrc))
           zip.extractall(r'{0}'.format(zipDir))

        except:
            return False

        return True

    def entropy(self, length):
        return ''.join(random.choice(string.ascii_lowercase) for i in range (length))

    def delete(self):
        shutil.rmtree(self.unzip_dir)
