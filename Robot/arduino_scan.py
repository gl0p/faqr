import serial.tools.list_ports


def get_ports():
    ports = serial.tools.list_ports.comports()

    return ports


def findArduino(portsFound):
    commPort = 'None'
    numConnection = len(portsFound)

    for i in range(0, numConnection):
        port = foundPorts[i]
        strPort = str(port)

        if 'Arduino' in strPort:
            splitPort = strPort.split(' ')
            commPort = (splitPort[0])
    return commPort


foundPorts = get_ports()
connectPort = findArduino(foundPorts)


def returned_port():
    return connectPort
