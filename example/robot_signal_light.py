
import time
import struct
import neopixel


class RSL:
    # RSL frequency
    RSL_FREQ = 5
    RSL_PERIOD = 1/RSL_FREQ

    # RSL colors
    RSL_ON = (0xff, 0x20, 0)
    RSL_OFF = (0, 0, 0)

    # States
    RSL_STATE_DISABLED = 0
    RSL_STATE_ENABLED_OFF = 1
    RSL_STATE_ENABLED_ON = 2

    def __init__(self, pin=None, num_pixels=None, pixels=None):
        self.state = self.RSL_STATE_DISABLED
        self.pixel_pin = pin
        self.num_pixels = num_pixels
        self.pixels = pixels

        if self.pin:
            self.pixels = neopixel.NeoPixel(
                self.pixel_pin, self.num_pixels, brightness=0.3,
                auto_write=False
            )

    def can_heartbeat_message(self, message):
        payload = struct.unpack("BBBBBBBB", message.data)
        # the ENABLED bit is in byte 5 (index 4) of the message, bit 1
        if payload[4] & 0x2 == 0:
            self.state = self.RSL_STATE_DISABLED
        else:
            self.state = self.RSL_STATE_ENABLED_OFF

    def iterate(self):
        if self.state == self.RSL_STATE_DISABLED:
            self.pixels.fill(self.RSL_OFF)
            self.pixels.show()
        else:
            _now = time.time()
            if _now > (self.rsl_time + self.RSL_PERIOD):
                if self.state == self.RSL_STATE_ENABLED_OFF:
                    self.pixels.fill(self.RSL_ON)
                    self.state = self.RSL_STATE_ENABLED_ON
                else:
                    self.pixels.fill(self.RSL_OFF)
                    self.state = self.RSL_STATE_ENABLED_OFF
                self.rsl_time = _now
            self.pixels.show()
