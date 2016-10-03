#!/usr/bin/env python

import pexpect
import time

from array import array
import bleTool as tool

Operation = {
    "01" : "START_DFU",
    "02" : "INITIALISE_DFU",
    "03" : "RECEIVE_FIRMWARE_IMAGE",
    "04" : "VALIDATE_FIRMWARE_IMAGE",
    "05" : "ACTIVATE_FIRMWARE_AND_RESET",
    "06" : "SYSTEM_RESET",
    "07" : "REPORT_RECEIVED",
    "08" : "PKT_RCPT_NOTIF_REQ",
    "10" : "RESPONSE",
    "11" : "PKT_RCPT_NOTIF",
}

Procedure = {
    "01" : "START",
    "02" : "INIT",
    "03" : "RECEIVE_APP",
    "04" : "VALIDATE",
    "07" : "IMAGE_SIZE_REQ",
    "08" : "PKT_RCPT_REQ",
}

Response = {
    "01" : "SUCCESS",
    "02" : "INVALID_STATE",
    "03" : "NOT_SUPPORTED",
    "04" : "DATA_SIZE",
    "05" : "CRC_ERROR",
    "06" : "OPER_FAILED",
}

class Command:
    START_DFU                    = 0x01
    INITIALISE_DFU               = 0x02
    RECEIVE_FIRMWARE_IMAGE       = 0x03
    VALIDATE_FIRMWARE_IMAGE      = 0x04
    ACTIVATE_FIRMWARE_AND_RESET  = 0x05
    SYSTEM_RESET                 = 0x06
    REPORT_RECEIVED              = 0x07
    PKT_RCPT_NOTIF_REQ           = 0x08

class Type:
    SOFT_DEVICE                  = 0x01
    BOOTLOADER                   = 0x02
    SOFT_DEVICE_BOOTLOADER       = 0x03
    APPLICATION                  = 0x04

class Init:
    RECEIVE                      = 0x00
    COMPLETE                     = 0x01

def arrayToHex(value):
    response = ""
    for val in value:
        response += "%02x" % val

    return response

def uint32ToArray(value):
    return [0,0,0,0,0,0,0,0,
           (value >> 0  & 0xFF),
           (value >> 8  & 0xFF),
           (value >> 16 & 0xFF),
           (value >> 24 & 0xFF)
    ]

def parseNotification(value):
    response = 0
    response += (int(value[3], 16) << 24)
    response += (int(value[2], 16) << 16)
    response += (int(value[1], 16) << 8)
    response += (int(value[0], 16) << 0)

    return response

class BleClient(object):
    def __init__(self, deviceAddr, debug=False):
        try:
            #Reset interface
            tool.resetInterface()

            self.deviceAddr = deviceAddr

            #Start gatttool
            self.connection = pexpect.spawn("gatttool -b '%s' -t random --interactive" % self.deviceAddr )
            if debug:
                self.connection.logfile = sys.stdout

            self.timeout = 10
            self.packetSize = 20

            self.dfuControlPoint = 0x10
            self.dfuPacket = 0x0e
            self.name = 0x03
            self.app = 0x1A

        except Exception as e:
            print(e)
            raise Exception("Error: BLE client initialisation failed")

    def connect(self):
        try:
            #print("Connecting...")

            self.connection.expect('\[LE\]>', self.timeout)
            self.connection.sendline('connect')
            self.connection.expect('Connection successful', self.timeout)

            #print("Connected")

        except Exception as e:
            print(e)
            raise Exception("Connecting failed")

    def disconnect(self):
        try:
            #print("Disconnecting...")

            self.connection.close()

            #print("Disconnected")

        except Exception as e:
            print(e)
            raise Exception("Disconnecting failed")

    def writeCharacteristic(self, handle, val, request=True):
        try:
            #print("Writing characteristic...")
            #print("char-write-req 0x%04x %s" % (handle , arrayToHex(val)))

            self.connection.expect('\[LE\]>', self.timeout)

            if request:
                self.connection.sendline("char-write-req 0x%04x %s" % (handle , arrayToHex(val)))
                self.connection.expect("Characteristic value was written successfully", self.timeout)
            else:
                self.connection.sendline("char-write-cmd 0x%04x %s" % (handle , arrayToHex(val)))

            #print("Writing successful")

        except Exception as e:
            print(e)
            raise Exception("Writing characteristic failed")

    def readCharacteristic(self, handle):
        try:
            #print("Reading characteristic...")
            #print("char-read-hnd 0x%04x" % (handle))

            self.connection.expect('\[LE\]>', self.timeout)
            self.connection.sendline("char-read-hnd 0x%04x" % (handle))
            self.connection.expect("Characteristic value/descriptor: ", self.timeout)
            response = self.connection.readline().split()
            parsedResponse = bytearray([int(x, 16) for x in response])

            #print("Reading successful")
            #print(parsedResponse)

            return parsedResponse

        except Exception as e:
            print(e)
            raise Exception("Reading characteristic failed")

    def waitForNotification(self):
        while True:
            try:
                #print("Waiting for notification...")

                self.connection.expect('Notification handle = .*? \r\n', self.timeout)
                response = self.connection.after.split()[3:][2:]
                response[0] = Operation[response[0]]
                if response[0] != "PKT_RCPT_NOTIF":
                    response[1] = Procedure[response[1]]
                    response[2] = Response[response[2]]

                #print("Received notification")

                return response

            except Exception as e:
                print(e)
                raise Exception("Waiting for notification failed")

    def updateDevice(self, binfile, datfile, progressUpdate=True, statusUpdate=True):
        try:
            self.progressUpdate = progressUpdate
            self.statusUpdate = statusUpdate
            self.start = 0

            if self.statusUpdate:
                print("Starting update...")

            self.binfile = binfile
            self.binarray = array('B', open(self.binfile, 'rb').read())
            self.size = len(self.binarray)

            self.datfile = datfile
            self.datArray = array('B', open(self.datfile, 'rb').read())

            #Connect to device
            self.connect()

            #Check whether device is in DFU mode
            if self.readName() != "DfuTarg":
                self.startBootloader()

            #Check FOTA status
            self.start = self.checkFota()
            if self.start == 0:
                self.initialiseFota()
            elif self.statusUpdate:
                print("Resuming FOTA")

            #Transfer FOTA
            self.transferFota()

            #Validate FOTA
            self.validateFota()

            #Finalise FOTA
            self.finaliseFota()

            if self.statusUpdate:
                print("Finished update")

            return True

        except Exception as e:
            print(e)
            return False
            #raise Exception("Update failed")

    def startBootloader(self):
        try:
            if self.statusUpdate:
                print("Starting bootloader...")

            #Enable DFU control point notifications
            self.writeCharacteristic(self.dfuControlPoint + 1, [Command.START_DFU, 0x00])

            #Start DFU mode
            self.writeCharacteristic(self.dfuControlPoint, [Command.START_DFU, Type.APPLICATION])

            #Allow time for device to restart
            time.sleep(1)

            #Re-connect to device
            self.connect()

            if self.statusUpdate:
                print("Started bootloader")

        except Exception as e:
            print(e)
            raise Exception("Starting bootloader failed")

    def checkFota(self):
        try:
            if self.statusUpdate:
                print("Checking FOTA...")

            #Enable DFU control point notifications
            self.writeCharacteristic(self.dfuControlPoint + 1, [Command.START_DFU, 0x00])

            #Request received image size
            self.writeCharacteristic(self.dfuControlPoint, [Command.REPORT_RECEIVED])

            #Check notification
            notification = self.waitForNotification()
            if notification[0] != "RESPONSE" or notification[1] != "IMAGE_SIZE_REQ" or notification[2] != "SUCCESS":
                raise Exception("Incorrect notification status")

            status = parseNotification(notification[3:])

            if self.statusUpdate:
                print("Checked FOTA")

            return status

        except Exception as e:
            print(e)
            raise Exception("checking FOTA failed")

    def initialiseFota(self):
        try:
            if self.statusUpdate:
                print("Initialising FOTA...")

            #Enable DFU control point notifications
            self.writeCharacteristic(self.dfuControlPoint + 1, [Command.START_DFU, 0x00])

            #Start DFU mode
            self.writeCharacteristic(self.dfuControlPoint, [Command.START_DFU, Type.APPLICATION])

            #Send binary image size
            self.writeCharacteristic(self.dfuPacket, uint32ToArray(self.size))

            #Check notification
            notification = self.waitForNotification()
            if notification[0] != "RESPONSE" or notification[1] != "START" or notification[2] != "SUCCESS":
                raise Exception("Incorrect notification status")

            #Send receive init image
            self.writeCharacteristic(self.dfuControlPoint, [Command.INITIALISE_DFU, Init.RECEIVE])

            #Send init image
            self.writeCharacteristic(self.dfuPacket, self.datArray)

            #Send complete init image
            self.writeCharacteristic(self.dfuControlPoint, [Command.INITIALISE_DFU, Init.COMPLETE])

            #Check notification
            notification = self.waitForNotification()
            if notification[0] != "RESPONSE" or notification[1] != "INIT" or notification[2] != "SUCCESS":
                raise Exception("Incorrect notification status")

            if self.progressUpdate:
                #Send packet receipt notification interval
                self.writeCharacteristic(self.dfuControlPoint, [Command.PKT_RCPT_NOTIF_REQ, 0x64, 0x00])

            #Send receive firmware image
            self.writeCharacteristic(self.dfuControlPoint, [Command.RECEIVE_FIRMWARE_IMAGE])

            if self.statusUpdate:
                print("Initialised FOTA")

        except Exception as e:
            print(e)
            raise Exception("Initialising FOTA failed")

    def transferFota(self):
        try:
            if self.statusUpdate:
                print("Transferring FOTA...")

            #Calculate block count
            blockCount = 1
            if self.start != 0:
                blockCount += (self.start / self.packetSize)

            #Status update
            if self.progressUpdate:
                percent = (float(self.start) / self.size) * 100.0
                print("Percent complete: %2.2f" % percent)

            #Send image
            for i in range(self.start, self.size, self.packetSize):
                #Send block
                block = self.binarray[i:i + self.packetSize]
                self.writeCharacteristic(self.dfuPacket, block, False)

                #Status update
                if self.progressUpdate and (blockCount % 100) == 0:
                    notification = self.waitForNotification()
                    if notification[0] != "PKT_RCPT_NOTIF":
                        raise Exception("Incorrect notification status")

                    #Calculate percentage
                    status = parseNotification(notification[1:])
                    percent = (float(status) / self.size) * 100.0
                    print("Percent complete: %2.2f" % percent)

                    #Check transfer is in sync
                    if (i + self.packetSize) != status:
                        raise Exception("Transfer out of sync")

                if self.progressUpdate:
                    blockCount += 1

            if self.progressUpdate:
                print("Percent complete: %2.2f" % 100.0)

            #Check notification
            notification = self.waitForNotification()
            if notification[0] != "RESPONSE" or notification[1] != "RECEIVE_APP" or notification[2] != "SUCCESS":
                raise Exception("Incorrect notification status")

            if self.statusUpdate:
                print("Transferred FOTA")

        except Exception as e:
            print(e)
            raise Exception("Transferring FOTA failed")

    def validateFota(self):
        try:
            if self.statusUpdate:
                print("Validating FOTA...")

            #Check correct amount of bytes were transferred
            if self.checkFota() != self.size:
                raise Exception("Bytes received does not match binary size")

            #Validate image
            self.writeCharacteristic(self.dfuControlPoint, [Command.VALIDATE_FIRMWARE_IMAGE])

            #Check notification
            notification = self.waitForNotification()
            if notification[0] != "RESPONSE" or notification[1] != "VALIDATE" or notification[2] != "SUCCESS":
                raise Exception("Incorrect notification status")

            if self.statusUpdate:
                print("Validated FOTA")

        except Exception as e:
            print(e)
            raise Exception("Validating FOTA failed")

    def finaliseFota(self):
        try:
            if self.statusUpdate:
                print("Finalising FOTA...")

            #Activate and reset
            self.writeCharacteristic(self.dfuControlPoint, [Command.ACTIVATE_FIRMWARE_AND_RESET])

            #Allow time for device to restart
            time.sleep(1)

            #Disconnected
            self.disconnect()

            if self.statusUpdate:
                print("Finalised FOTA")

        except Exception as e:
            print(e)
            raise Exception("Finalising FOTA failed")

    def readName(self):
        try:
            response = self.readCharacteristic(self.name)
            return "".join(map(chr, response))

        except Exception as e:
            print(e)
            raise Exception("Reading name failed")

    def readApp(self):
        try:
            response = self.readCharacteristic(self.app)
            return "".join(map(chr, response))

        except Exception as e:
            print(e)
            raise Exception("Reading app failed")
