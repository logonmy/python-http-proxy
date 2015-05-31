import socket
import argparse
import threading
import re

templates = []

def server(client_socket):
    global templates
    buffer = b''
    flag = False
    content_length = None
    content_index = 0
    host = None
    port = None
    while True:
        buffer += client_socket.recv(1024)
        if buffer[-4:] == b'\r\n' * 2:
            http_response = re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", buffer.decode('utf-8'))
            for i in http_response:
                if i[0].lower() == 'content-length':
                    content_length = int(i[1])
                if i[0].lower() == 'host':
                    host_info = i[1].split(':')
                    if len(host_info) == 2:
                        port = host_info[1]
                    host = host_info[0]
            if content_length is None:
                break
        if content_length is not None:
            content_index += 1
            if content_index > content_length:
                break
    if port is None:
        port = 80
    for i in templates:
        template = r'{}'.format(i)
        match = re.search(template, host)
        if match:
            client_socket.send(b'423 Locked\r\nhost:' + bytes(host.encode()) + b'\r\n')
            flag = True
            break
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_data = b''
    server_address = socket.gethostbyname(host)
    proxy_socket.connect((server_address, port))
    proxy_socket.send(buffer)
    # print(host, buffer)
    try:
        tmp = proxy_socket.recv(1024)
        while tmp:
            proxy_data += tmp
            tmp = proxy_socket.recv(1024)
        if not flag:
            client_socket.send(proxy_data)
    except ConnectionResetError:
        pass
    # client_socket.close()
    # proxy_socket.close()


def add_domain():
    global templates
    while True:
        action = int(input())
        if action == 1:
            print("regexp:")
            templates.append(input())
        if action == 2:
            print("All templates:")
            for i in templates:
                print(i + ' ')


def main():
    global templates
    parser = argparse.ArgumentParser(description="Simple PROXY server on python")
    parser.add_argument('port', help='port')
 
    args = parser.parse_args()
    port = int(args.port)

    print('write 1 to add new regexp template \nwrite 2 to show all regexp templates')
 
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind(('', port))
    proxy_socket.listen(5)

    threading.Thread(target=add_domain, args=()).start()

    while True:
        sock, _ = proxy_socket.accept()
        threading.Thread(target=server, args=(sock,)).start()
 
    proxy_socket.close()
 

if __name__ == '__main__':
    main()
