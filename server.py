import serial

ser = serial.Serial('/dev/tty.usbmodem1451', 115200)

while True:
    print ser.readline()



def setArguments():
    pass

def