import serial

ser = serial.Serial('/dev/ttyACM0', 9600)

while True:
	line = ser.readline().decode('utf-8').strip()
	print("Received:", line)
