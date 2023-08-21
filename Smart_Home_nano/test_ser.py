import serial 
import time
ser = serial.Serial('/dev/ttyUSB0',baudrate= 9600,timeout=0.5)
data = [[0x2C],[0x12],[0x02],[0x02],[0x5B]]
#while True:
for i in range(len(data)):
    data[i] = bytearray(data[i])
    time.sleep(0.5)
    ser.write(data[i])
print('finished')

time.sleep(10)

data = [[0x2C],[0x12],[0x02],[0x03],[0x5B]]
for i in range(len(data)):
    data[i] = bytearray(data[i])
    time.sleep(0.1)
    ser.write(data[i])
    print(data[i])
print('finished')

