#!/usr/bin/env python

import pexpect
import time
import re

def resetInterface():
    try:
        connection = pexpect.spawn("hciconfig hci0 down")
        time.sleep(1)
        connection = pexpect.spawn("hciconfig hci0 up")
        time.sleep(1)

    except Exception as e:
        print(e)
        raise Exception("Error: BLE reset interface failed")

def scan(timeout=10):
    try:
        resetInterface()

        connection = pexpect.spawn("timeout %d hcitool lescan" % timeout)
        connection.expect("LE Scan \.+", timeout)

        output = ""
        line_pat = "(?P<addr>([0-9A-F]{2}:){5}[0-9A-F]{2}) (?P<name>.*)"

        while True:
            try:
                res = connection.expect(line_pat)
                output += connection.after
            except pexpect.EOF:
                break

        lines = re.split('\r?\n', output.strip())
        lines = list(set(lines))
        lines = [line for line in lines if re.match(line_pat, line)]
        lines = [re.match(line_pat, line).groupdict() for line in lines]
        lines = [line['addr'] for line in lines if re.match("resin", line['name'])]

        return lines

    except Exception as e:
        print(e)
        raise Exception("Error: BLE scanning failed")

def online(addr, timeout=10):
    try:
        resetInterface()

        connection = pexpect.spawn("timeout %d hcitool lescan" % timeout)
        connection.expect("LE Scan \.+", timeout)

        output = ""
        line_pat = "(?P<addr>([0-9A-F]{2}:){5}[0-9A-F]{2}) (?P<name>.*)"

        while True:
            try:
                res = connection.expect(line_pat)
                output = connection.after
                output.strip()

                if re.match(line_pat, output):
                    output = re.match(line_pat, output).groupdict()
                    if re.match("resin", output['name']) and re.match(addr, output['addr']):
                        return True

            except pexpect.EOF:
                return False

    except Exception as e:
        print(e)
        raise Exception("Error: BLE online failed")
