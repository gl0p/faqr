from Neo import easyGpio
from time import sleep

pin = easyGpio(13)  # Pin 2 with LED

pin.pinOUT()  # Make pin output

while True:
    pin.on()  # Turn pin on
    sleep(1)  # wait one second
    pin.off()  # Turn pin off
    sleep(1)


