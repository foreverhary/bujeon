import socket
import select

HOST = '127.0.0.1'
PORT = 1025
ADDR = (HOST, PORT)
SIZE = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(ADDR)
    s.listen()
    print('server start!!!')

    readsocks = [s]
    answers = {}

    while True:
        readables, writables, exceptions = select.select(readsocks, [], [])
        for sock in readables:
            if sock == s:
                newsock, addr = s.accept()
                readsocks.append(newsock)
            else:
                conn = sock
                try:
                    data = conn.recv(SIZE)
                    data = data.decode('utf-8')
                    print(data)
                    if data == '500000FF03FF000018000404010001B*0000320001':
                        conn.send('D00000FF03FF00000C000010000000'.encode())
                    elif data == '500000FF03FF000018000404010001B*0000320002':
                        conn.send('D00000FF03FF00000C000010000000'.encode())
                    elif '500' in data:
                        conn.send('D00000FF03FF0000040000'.encode())
                    else:
                        readsocks.remove(sock)
                except UnicodeDecodeError:
                    print(data)
                    if data[11:13] == b'\x01\x04':
                        conn.send(b'\xD0\x00\x00\xFF\xFF\x03\x00\x06\x00\x00\x00\x10\x00\x00\x00')
                    elif data[11:13] == b'\x01\x14':
                        conn.send(b'\xD0\x00\x00\xFF\xFF\x03\x00\x06\x00\x00\x00\x10\x00\x00\x00')
                    else:
                        readsocks.remove(sock)
