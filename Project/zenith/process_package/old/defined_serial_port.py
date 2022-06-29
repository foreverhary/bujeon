import serial.tools.list_ports
from PySide2.QtSerialPort import QSerialPortInfo
from serial import SerialException, Serial

ports = [s.device for s in serial.tools.list_ports.comports()]
ports.sort()


def get_serial_available_list():
    return [port.portName()
            for port in QSerialPortInfo.availablePorts()
            if not port.isBusy()]


def connect_serial(ser, port, button):
    try:
        if ser.isOpen():
            ser.close()
            button.set_background_color('red')
        else:
            ser.port = port
            ser.open()
            button.set_background_color('blue')
            ser.flushInput()
            return True
    except SerialException:
        button.set_background_color(color='red')
    return False


def serial_flush(ser):
    ser.flushInput()
    ser.flushOutput()


if __name__ == '__main__':
    print(get_serial_available_list(ports))
