import time
import serial

ser = serial.Serial()
ser.port = 'com4'
ser.baudrate = 115200

while True:
    try:
        if not ser.isOpen():
            ser.open()
        send_data = ''
        for index in range(5):
            send_data += f"{index + 1},"
        send_data = send_data[:-1] + '\n'
        ser.write(send_data.encode())
        time.sleep(0.5)
    except serial.SerialException as e:
        print(e)
        ser.close()
