# Microsoft Windows only, implemented by Win32API
import ctypes
import ctypes.wintypes

# Origin is at the top-left of the screen
EVENT_MOUSE_MOVE = 0x0001
EVENT_MOUSE_LCLICK = 0x0002 | 0x0004
EVENT_MOUSE_RCLICK = 0x0008 | 0x0010
EVENT_MOUSE_MCLICK = 0x0020 | 0x0040
EVENT_MOUSE_WHEEL = 0x0800

EVENT_KEY_DOWN = 0x0000
EVENT_KEY_UP = 0x0002


def get_screen_size():
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    return (screen_width, screen_height)


def get_cursor_pos():
    cursor = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return (cursor.x, cursor.y)


# relative unit: mickey
# absolute unit: pixel
def send_mouse_event(event, x, y, is_abs=False, data=0):
    if event is EVENT_MOUSE_WHEEL:
        data = ctypes.c_long(-int(data))
    else:
        data = ctypes.c_long(0)
    if event is EVENT_MOUSE_MOVE:
        cur_x, cur_y = get_cursor_pos()
        scr_w, scr_h = get_screen_size()
        if is_abs is True:
            x = 65535 * (x / scr_w)
            y = 65535 * (y / scr_h)
            event = event | 0x8000
        x = ctypes.c_long(int(x))
        y = ctypes.c_long(int(y))
        ctypes.windll.user32.mouse_event(event, x, y, data)
    else:
        cur_x, cur_y = get_cursor_pos()
        send_mouse_event(EVENT_MOUSE_MOVE, x, y, is_abs)
        ctypes.windll.user32.mouse_event(event, x, y, data)
        send_mouse_event(EVENT_MOUSE_MOVE, cur_x, cur_y, True)


def send_mouse_scroll(step, x=None, y=None):
    if x is None or y is None:
        scr_w, scr_h = get_screen_size()
        x = scr_w // 2
        y = scr_h // 2
    send_mouse_event(EVENT_MOUSE_WHEEL, x, y, True, step)


def get_vk_fn(func_num):
    if func_num < 0 or func_num > 12:
        func_num = 0
    return 0x70 + (func_num - 1)


VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3

VK_BROWSER_BACK = 0xA6
VK_BROWSER_FORWARD = 0xA7
VK_BROWSER_REFRESH = 0xA8
VK_BROWSER_STOP = 0xA9
VK_BROWSER_SEARCH = 0xAA
VK_BROWSER_FAVORITES = 0xAB
VK_BROWSER_HOME = 0xAC


def send_keyboard_event(vk):
    ctypes.windll.user32.keybd_event(vk, 0, EVENT_KEY_DOWN, 0)
    ctypes.windll.user32.keybd_event(vk, 0, EVENT_KEY_UP, 0)


if __name__ == '__main__':
    send_keyboard_event(VK_MEDIA_PREV_TRACK)
