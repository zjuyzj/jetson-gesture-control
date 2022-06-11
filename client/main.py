import automation as ctrl
from network import UDP_Client
import time


def ctrl_callback(msg: str):
    print('Command: ', msg.split(' ')[0])
    if msg == 'mute':
        ctrl.send_keyboard_event(ctrl.VK_VOLUME_MUTE)
    elif msg == "pause":
        ctrl.send_keyboard_event(ctrl.VK_MEDIA_PLAY_PAUSE)
    elif msg == "prev":
        ctrl.send_keyboard_event(ctrl.VK_MEDIA_PREV_TRACK)
    elif msg == "next":
        ctrl.send_keyboard_event(ctrl.VK_MEDIA_NEXT_TRACK)
    elif msg == 'vol_up':
        for _ in range(5):
            ctrl.send_keyboard_event(ctrl.VK_VOLUME_UP)
    elif msg == 'vol_down':
        for _ in range(5):
            ctrl.send_keyboard_event(ctrl.VK_VOLUME_DOWN)


if __name__ == '__main__':
    client = UDP_Client()
    while not client.is_connect():
        addr = client.connect()
        if addr is not None:
            print("Found Jetson Nano at: ", addr)
            client.recv_msg(ctrl_callback)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
            break
