import Jetson.GPIO as GPIO
import time


class Distance:
    def __init__(self, trig_pin=31, echo_pin=33):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        GPIO.setup(self.trig_pin, GPIO.OUT)  # Trig
        GPIO.setup(self.echo_pin, GPIO.IN)  # Echo

    def _get_dist(self):
        GPIO.output(self.trig_pin, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.trig_pin, GPIO.HIGH)
        time.sleep(0.000010)
        GPIO.output(self.trig_pin, GPIO.LOW)
        while not GPIO.input(self.echo_pin):
            pass
        t1 = time.time()
        while GPIO.input(self.echo_pin):
            pass
        t2 = time.time()
        return (t2-t1)*340*100/2

    def get_dist(self):
        temp = self._get_dist()
        while temp > 120:
            temp = self._get_dist()
        return temp

    def disconnect(self):
        GPIO.cleanup()
