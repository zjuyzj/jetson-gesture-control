import socket
import threading
import time


class UDP_Client:
    def __init__(self, port=1234):
        self.send_socket = None
        self.server_ip = None
        self.recv_socket = None
        self.recv_callback = None
        self.recv_thread = None
        self.port = port

    def is_connect(self):
        return (self.server_ip is not None)

    def connect(self, repeat=10, interval=1):
        connected = False
        s_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_listen.bind(('', self.port))
        s_listen.settimeout(1)
        for _ in range(repeat):
            try:
                data, s_addr = s_listen.recvfrom(1024)
                if data.decode() == '__search__':
                    s_res = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s_res.sendto('__connect__'.encode(),
                                 (s_addr[0], self.port + 1))
                    s_res.close()
                    connected = True
                    break
            except socket.timeout:
                time.sleep(interval)
        s_listen.close()
        if connected:
            self.recv_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self.recv_socket.bind(('', self.port))
            self.send_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self.server_ip = s_addr[0]
        return self.server_ip if connected else None

    def _thread_recv_msg(self):
        while True:
            if self.recv_socket is None:
                return
            else:
                data, _ = self.recv_socket.recvfrom(1024)
                self.recv_callback(data.decode())

    def recv_msg(self, callback):
        if self.recv_thread is not None:
            return
        self.recv_callback = callback
        self.recv_thread = threading.Thread(target=self._thread_recv_msg)
        self.recv_thread.setDaemon(True)
        self.recv_thread.start()

    def send_msg(self, msg):
        if self.send_socket is None:
            return
        self.send_socket.sendto(msg.encode(), (self.server_ip, self.port + 1))

    def disconnect(self):
        self.send_socket.sendto(
            '__bye__'.encode(), (self.server_ip, self.port + 1))
        self.send_socket.close()
        self.send_socket = None
        self.recv_socket.close()
        self.recv_socket = None
