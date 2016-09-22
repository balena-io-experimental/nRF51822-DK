#!/usr/bin/env python

import os
import sys
import optparse
import time

from unpacker import Unpacker
from bleClient import BleClient
from array import array

def main():
    try:
        parser = optparse.OptionParser(usage='%prog -a <Device_address> -z <Zip_file>\n\nExample:\n\tupdate.py -a cd:e3:4a:47:1c:e4 -z application.zip')

        parser.add_option('-a', '--address',
            action='store',
            dest="deviceAddr",
            type="string",
            default=None
            )

        parser.add_option('-z', '--zip',
            action='store',
            dest="zipfile",
            type="string",
            default=None
            )

        options, args = parser.parse_args()

    except Exception as e:
        print(e)
        print("For help use --help")

    try:
        if (not options.deviceAddr):
            print("Error: Device address not passed in")
            print("For help use --help")
        elif (not options.zipfile):
            print("Error: Zip file not passed in")
            print("For help use --help")
        elif not os.path.isfile(options.zipfile):
            print("Error: Zip file not found")
            print("For help use --help")

        unpacker = Unpacker()
        binfile, datfile = unpacker.unpack(options.zipfile)

        bleClient = BleClient(options.deviceAddr.upper())
        bleClient.updateDevice(binfile, datfile)

    except Exception as e:
        print(e)
        print("For help use --help")

if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
