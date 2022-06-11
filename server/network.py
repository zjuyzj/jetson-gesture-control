import socket
import threading
import time


class UDP_Server:
    def _get_local_ip_addr(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('www.baidu.com', 80))
            ip_addr = s.getsockname()[0]
        finally:
            s.close()
        return ip_addr

    def __init__(self, port=1234):
        self.local_ip = self._get_local_ip_addr()
        self.port = port
        self.client_ip = None
        self.send_socket = None
        self.monitor_socket = None
        self.monitor_thread = None

    def _thread_monitor(self):
        while True:
            try:
                data, _ = self.monitor_socket.recvfrom(
                    1024, socket.MSG_DONTWAIT)
                if data.decode() == '__bye__':
                    self.client_ip = None
                    self.monitor_socket.close()
                    self.monitor_socket = None
                    self.send_socket.close()
                    self.send_socket = None
                    print("PC Disconnected")
                    return
            except BlockingIOError:
                time.sleep(1)

    def is_connect(self):
        return (self.client_ip is not None)

    def connect(self, repeat=10, interval=1):
        connected = False
        # Set socket for broadcast
        net_addr_idx = self.local_ip.rindex('.')
        broadcast_addr = self.local_ip[:net_addr_idx] + '.255'
        s_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST |
                               socket.SO_REUSEADDR, True)
        # Set socket for listening (blocking with timeout)
        s_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_listen.bind(('', self.port + 1))
        s_listen.setblocking(True)
        s_listen.settimeout(1)
        # Broadcast Jetson's ipv4 addr for #repeat times
        for _ in range(repeat):
            s_broadcast.sendto('__search__'.encode(),
                               (broadcast_addr, self.port))
            # Try to get the PC's addr response each broadcast
            try:
                data, s_addr = s_listen.recvfrom(1024)
                if data.decode() == '__connect__':
                    s_listen.close()
                    connected = True
                    self.client_ip = s_addr[0]
                    break
            except socket.timeout:
                time.sleep(interval)
        s_broadcast.close()
        if connected:
            self.monitor_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self.monitor_socket.bind(('', self.port+1))
            self.monitor_socket.setblocking(False)  # non-blocking socket
            self.monitor_thread = threading.Thread(target=self._thread_monitor)
            self.monitor_thread.setDaemon(True)
            self.monitor_thread.start()
            self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self.client_ip if connected else None

    def send_msg(self, msg):
        if self.send_socket is None:
            return False
        self.send_socket.sendto(msg.encode(), (self.client_ip, self.port))
        return True
