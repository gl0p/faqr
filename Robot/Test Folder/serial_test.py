import serial
from usb_scan import main
from time import sleep
usb_path = main()

data = 0
serial_data = ""

sr = serial.Serial(port=str('/dev/ttyS1'),
                            baudrate=115200,
                            parity=serial.PARITY_NONE,
                            bytesize=serial.EIGHTBITS,
                            timeout=0)
while True:
    while sr.inWaiting() > 0:
        serail_data = sr.readline()
        serial_data = str(serail_data.decode())
        if 'sending_data' in serial_data:
            serial_data = serial_data.replace('sending_data', '')
            print('Serial Data Recieved:', serail_data)
            sleep(0.5)
            sr.write('{} \n'.format('data_rec').encode('utf-8'))
        if 'data_rec' in serial_data:
            data = data+1
            break
    sr.write('{} '.format('sending_data').encode('utf-8'))
    sr.write('{} \n'.format(data).encode('utf-8'))
    print('Sending Data:', data)
    sleep(1)
