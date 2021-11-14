import socket
import select
import errno

from PyQt5.QtWidgets import QApplication
# from clientui import MainWindow

import sys

HEADER_LENGTH = 10

IP = '127.0.0.1'
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect(username):
    # Connect to a given ip and port
    client_socket.connect((IP, PORT))

    # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
    client_socket.setblocking(False)

    username = username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')

    client_socket.send(username_header + username)

def send_message(destiny, message):
    if message and destiny:
        destiny_username_enc = destiny.encode('utf-8')
        destiny_header = f'{len(destiny):<{HEADER_LENGTH}}'.encode('utf-8')

        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(destiny_header + destiny_username_enc + message_header + message)
    
def get_messages():
    message_list = []
    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()
            
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            message_list.append({'username': username, 'message': message})

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        return message_list

    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()