import serial
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM5'
print(ser.name)
data = open("data.txt", 'r+')
#data = open("test.csv", 'r+')
#xPos = []
#xPos = list()
#yPos = []
#yPos = list()
#rad = []
#rad = list()
#zPos = []
#zPos = list()
ser.open()
line = ser.readline() #stores one line of serial input to a string
while line != "":
    line = ser.readline()
    data.write(line)
    print(line)
    #if len(line.split(",")) == 4:
        #x,y,r,z = line.split(",")#parses string and stores in vars
        #xPos.append(float(x))
        #yPos.append(float(x))
        #rad.append(float(r))
        #zPos.append(float(z))
        #print(x) 

data.close()
ser.close()
