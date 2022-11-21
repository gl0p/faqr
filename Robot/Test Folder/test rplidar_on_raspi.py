import serial
from time import sleep
import json
ser = serial.Serial(port='/dev/raspi_02w',
                         baudrate=115200,
                         parity=serial.PARITY_NONE,
                         bytesize=serial.EIGHTBITS,
                         write_timeout=1)


def send(data):
    ser.write('{} \n'.format(data).encode("utf-8"))
    sleep(0.25)


def read():
    while ser.inWaiting() > 0:
        data = ser.readline()
        data = data.decode()
        data = eval(data)
        print(type(data), data)


send('get_ort')
read()
# sleep(2)
# send('get_dian')
# read()
# sleep(2)
# send('motor_off')
# read()
# sleep(2)
# send('motor_on')
# read()
# sleep(5)
# send('get_pos')
# read()
# sleep(2)
# send('get_dian')
# read()
# sleep(5)
# send('motor_off')
# read()


