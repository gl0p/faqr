import serial
from time import sleep

ser = serial.Serial(port='/dev/ttyACM0',
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    bytesize=serial.EIGHTBITS,
                    write_timeout=1)
ser.write(str("red").encode('utf-8'))

