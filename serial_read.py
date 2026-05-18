#!/usr/bin/env python3
"""Read ESP32 serial output non-interactively."""
import serial
import sys
import time

port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbserial-0001"
baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
duration = int(sys.argv[3]) if len(sys.argv) > 3 else 15

ser = serial.Serial(port, baud, timeout=1)
ser.dtr = False  # reset ESP32
ser.rts = True
time.sleep(0.1)
ser.rts = False   # release reset
time.sleep(0.1)
ser.reset_input_buffer()

start = time.time()
while time.time() - start < duration:
    line = ser.readline()
    if line:
        try:
            print(line.decode("utf-8", errors="replace").rstrip())
        except:
            print(repr(line))
    sys.stdout.flush()

ser.close()
