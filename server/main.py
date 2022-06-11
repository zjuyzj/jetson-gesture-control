import time
from network import UDP_Server
from distance import Distance
from camera import Camera
# from pose.classifier import Classifier
from tsm.classifier import Classifier

prev_gesture = 'no hand'
valid_gesture = ''
gesture_cnt = 0

gesture_to_send = []

dist = Distance()
server = UDP_Server()


def parse_gesture(gesture):
    if gesture == "Pushing Hand Away":
        gesture_to_send.append('mute')
    elif gesture == "Shaking Hand":
        gesture_to_send.append('pause')
    elif gesture == "Swiping Left":
        gesture_to_send.append('prev')
    elif gesture == "Swiping Right":
        gesture_to_send.append('next')
    elif gesture == "Swiping Up":
        gesture_to_send.append('vol_up')
    elif gesture == "Swiping Down":
        gesture_to_send.append('vol_down')
    # elif gesture == "Stop Sign":
    #     dist_cm = dist.get_dist()
    #     gesture_to_send.append('set_vol '+str(dist_cm))


def res_callback(gesture):
    global valid_gesture, prev_gesture, gesture_cnt
    if gesture == prev_gesture:
        gesture_cnt += 1
    else:
        gesture_cnt = 0
    if gesture_cnt == 4:
        gesture_cnt = 0
        if valid_gesture != prev_gesture:
            parse_gesture(prev_gesture)
            valid_gesture = prev_gesture
    prev_gesture = gesture


classifier = Classifier(result_callback=res_callback)

# For TRT-Pose
# camera = Camera(cam_callback=classifier.classify_callback)

# For TSM
camera = Camera(cam_callback=classifier.classify_callback,
                h=320, w=240, fps=15)

if __name__ == '__main__':
    camera.start()
    try:
        while True:
            if not server.is_connect():
                addr = server.connect()
                if addr is not None:
                    print("Found PC at: ", addr)
            elif len(gesture_to_send) != 0:
                server.send_msg(gesture_to_send[0])
                gesture_to_send.pop(0)
            time.sleep(1)
    except KeyboardInterrupt:
        camera.stop()
        dist.disconnect()
        exit(0)
