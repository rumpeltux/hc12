#!/usr/bin/env python3
import serial
import time

def setBaud(hc, rate):
    hc.write(b'AT+B%d' % rate)
    ok = b'OK+B%d\r\n' % rate
    resp = hc.read(len(ok))
    assert resp == ok, (ok, resp)

def enterUpdateMode(tty):
    """Enter the firmware update mode."""
    hc = serial.Serial(tty, 9600, timeout=.1)
    hc.write(b'AT+UPDATE\n')
    x = hc.read(40)
    assert b'OK\r\n' in x, repr(x)
    time.sleep(.1)
    hc.write(b'\xEE')
    hc.close()
    time.sleep(.00001)
    hc = serial.Serial(tty, 19200, timeout=.1)
    hc.write(b'I')
    x = hc.read(100)
    assert x == b'\4', repr(x)
    return hc

# DUMPCODE below contains the following
# raw assembly that will dump the firmware when executed.
_dump_code = bytes.fromhex(
    'AE 80 00' # x = 0x8000
    'A608 C75235' # UART_CR2 = TEN
    '905F 90BFF4' # tickle watchdog
    '720F52 30 FB' # while(!(UART_SR & TXE)) ;
    'F6 C75231' # UART_DR = x
    '5C' # x++
    '26EF' # loop
    '81' # ret
)

DUMPCODE = bytes.fromhex('25008ba093d481ae4200a608c7b235905f90bff47e0f5230fbf67852315c26ef84841701be')

def dumpFirmware(hc, filename):
    hc.write(b'AT+VER')
    resp = hc.read(19)
    expected = b'www.hc01.com  HC-12'
    if resp != expected:
      print('Warning, expected %s but got %s' % (repr(expected), repr(resp)))

    out = open(filename, 'wb')
    print('Dumping firmware to %s...' % args.filename)
    bytes_read = 0
    chunk_size = 128
    total_len = 0x8000
    while bytes_read < total_len:
      data = hc.read(chunk_size)
      if len(data) < chunk_size:
        print('\nERROR: read %d instead of %d' % (len(data), chunk_size))
        print('Please try again.')
      out.write(data)
      print('% 2.1f%%' % (bytes_read * 100 / total_len), end='\r', flush=True)
      bytes_read += chunk_size
    print('\nDone :-)')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", default='/dev/ttyUSB0',
                      help="The serial device the HC is connected to")
    parser.add_argument("-f", "--filename", default='hc12-fw.bin',
                      help="The filename to which to dump the firmware")
    parser.add_argument("-n", "--no-flash", action='store_true',
                      help="Do not attempt to flash the dumping code (use this if you've already done so)")
    args = parser.parse_args()

    if not args.no_flash:
      # We only do this to ensure we're actually talking to the right device.
      hc = serial.Serial(args.device, 9600, timeout=.1)
      print('Switching baudrate to 9600...')
      try:
        setBaud(hc, 9600)
      except AssertionError as e:
        print('Failed to set baud rate. Make sure that the SET pin is pulled to GND.')
        raise
      hc.close()

      print('Flashing dumpcode...')
      hc = enterUpdateMode(args.device)
      hc.write(DUMPCODE)
      resp = hc.read(1)
      assert resp == b'\xE0', resp
      hc.close()
      
      print('Please reset the HC-12 (e.g. by turning power off and on). Press ENTER when done',
            end='', flush=True)
      input()
    hc = serial.Serial(args.device, 9600, timeout=1)
    dumpFirmware(hc, args.filename)
