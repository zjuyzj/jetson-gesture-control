from jetcam.usb_camera import USBCamera
from jetcam.csi_camera import CSICamera


class Camera:
    def __init__(self, cam_callback, is_csi_cam=True, dev_id=1, w=224, h=224, fps=10):
        self.cam_callback = cam_callback
        if is_csi_cam:
            self.camera = CSICamera(width=w, height=h, capture_fps=fps)
        else:
            self.camera = USBCamera(
                width=w, height=h, capture_fps=fps, capture_device=dev_id)

    def start(self):
        self.camera.running = True
        self.camera.observe(self.cam_callback, names='value')

    def stop(self):
        self.camera.running = False
        self.camera.unobserve_all()
        self.camera.cap.release()
