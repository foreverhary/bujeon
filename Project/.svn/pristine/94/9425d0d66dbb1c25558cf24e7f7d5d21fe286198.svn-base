import serial.tools.list_ports
from serial import SerialException, Serial

ports = [s.device for s in serial.tools.list_ports.comports()]
ports.sort()


def get_serial_available_list(serial_ports):
    available_serial_list = []
    for port in serial_ports:
        try:
            s = Serial(port)
            available_serial_list.append(port)
            s.close()
        except SerialException:
            pass
    return available_serial_list


def connect_serial(ser, port, button):
    try:
        if ser.isOpen():
            ser.close()
            button.set_clicked('red')
        else:
            ser.port = port
            ser.open()
            button.set_clicked('blue')
            ser.flushInput()
            return True
    except SerialException:
        button.set_clicked(color='red')
    return False


def serial_flush(ser):
    ser.flushInput()
    ser.flushOutput()


if __name__ == '__main__':
    print(get_serial_available_list(ports))
