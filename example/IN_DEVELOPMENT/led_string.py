
import math
import time
import neopixel
from can_carrier_board import CANCarrierBoard


class LED_STRING:
    RED = (255, 0, 0)      # Red
    GREEN = (0, 255, 0)    # Green
    BLACK = (0, 0, 0)      # Black
    YELLOW = (255, 255, 0) # Yellow
    ORANGE = (1,2,3) # FiX LATER

    def __init__(self, num_leds=None, led_pixels_per_m=0, sensor=None):
        self.sensor = sensor
        # cm per pixel
        self.pixel_density = 100 / led_pixels_per_m
        if num_leds:
            self.num_leds = num_leds
        else:
            self.num_leds = math.ceil(self.sensor.real_sensor_distance / self.pixel_density)

        # LED string
        carrier_board = CANCarrierBoard()
        _carrier_pixel_pin = carrier_board.NEOPIXEL
        self.carrier_pixel = neopixel.NeoPixel(_carrier_pixel_pin, self.num_leds, brightness=0.3, auto_write=False)
        self.carrier_pixel.fill(self.YELLOW)
        self.carrier_pixel.show()
        time.sleep(1)

    def not_detected(self):
        self.carrier_pixel.fill(self.RED)
        self.carrier_pixel.show()

    def calibrating(self):
        self.carrier_pixel.fill(self.ORANGE)
        self.carrier_pixel.show()

    def detected(self):
        left_led_index = int((self.sensor.left_distance / self.sensor.left_distance_max) * self.num_leds)
        right_led_index = self.num_leds - int((self.sensor.right_distance / self.sensor.right_distance_max) * self.num_leds)
        self.carrier_pixel.fill(self.BLACK)
        for i in range(left_led_index, right_led_index):
            self.carrier_pixel[i] = self.GREEN
        print("..detected")
        self.carrier_pixel.show()
