
import struct
import time
import canio
import neopixel
import adafruit_vl53l4cd
from frc_can import FRCCANDevice
from can_carrier_board import CANCarrierBoard


class INTAKE_SENSOR_2023:
    INTAKE_SENSOR_2023_DISTANCE = 1
    INTAKE_SENSOR_2023_FILTER_ENABLE = 2
    INTAKE_SENSOR_2023_FILTER_DISABLE = 3

    STATE_OBJECT_NOT_DETECTED = 0
    STATE_OBJECT_DETECTED = 2

    OBJECT_THRESHOLD = 25.0

    def __init__(self, i2c, device_number=1, filter=False, debug=False):
        self.distance_message = FRCCANDevice(
            device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
            manufacturer=FRCCANDevice.MANUFACTURER_TEAM_USE,
            api=self.INTAKE_SENSOR_2023_DISTANCE,
            device_number=device_number)

        self.debug = debug
        self.filter = filter

        self.i2c = i2c
        self.vl53 = adafruit_vl53l4cd.VL53L4CD(self.i2c)

        # OPTIONAL: can set non-default values
        self.vl53.inter_measurement = 0
        self.vl53.timing_budget = 200

        print("VL53L4CD Simple Test.")
        print("--------------------")
        model_id, module_type = self.vl53.model_info
        print("Model ID: 0x{:0X}".format(model_id))
        print("Module Type: 0x{:0X}".format(module_type))
        print("Timing Budget: {}".format(self.vl53.timing_budget))
        print("Inter-Measurement: {}".format(self.vl53.inter_measurement))
        print("--------------------")
        print("MessageID {:08x}".format(self.distance_message.message_id))
        print("--------------------")

        self.vl53.start_ranging()

        while not self.vl53.data_ready:
            pass
        self.vl53.clear_interrupt()
        if self.vl53.distance > self.OBJECT_THRESHOLD:
            self.state = self.STATE_OBJECT_NOT_DETECTED
        else:
            self.state = self.STATE_OBJECT_DETECTED

        carrier_board = CANCarrierBoard()
        _carrier_pixel_pin = carrier_board.NEOPIXEL
        _num_carrier_pixels = 40
        self.carrier_pixel = neopixel.NeoPixel(_carrier_pixel_pin, _num_carrier_pixels, brightness=0.3, auto_write=False)

    def filter_enable(self, message):
        self.filter = True

    def filter_disable(self, message):
        self.filter = False

    def iterate(self):
        # wait for a reading
        while not self.vl53.data_ready:
            pass
        self.vl53.clear_interrupt()
        _distance = self.vl53.distance

        # This is where we should filter.. and keep state.
        # Two states: OBJECT_CAPTURED, OBJECT_MISSING
        # if missing and 2 samples with distance < X goto OBJECT_CAPTURED and send message
        # if captured and 2 samples with deistance > X goto OBJECT_missing and send message
        if self.filter:
            _send_message = False
            if self.state > self.STATE_OBJECT_NOT_DETECTED:
                if self.vl53.distance > self.OBJECT_THRESHOLD:
                    self.state -= 1
                    if self.state == self.STATE_OBJECT_NOT_DETECTED:
                        _send_message = True
            else:
                if self.vl53.distance <= self.OBJECT_THRESHOLD:
                    self.state += 1
                    if self.state == self.STATE_OBJECT_DETECTED:
                        _send_message = True
        else:
            _send_message = True

        if _distance >= 50:
            _color = (255, 0, 0)
        elif _distance > 35.0 and _distance < 50.0:
            _color = (255, 0, 255)
        else:
            _color = (0, 255, 0)
        self.carrier_pixel.fill(_color)
        self.carrier_pixel.show()

        if _send_message:
            msg_body = struct.pack("@f", _distance)
            message = canio.Message(id=self.distance_message.message_id,
                                data=msg_body,
                                extended=True)
            if self.debug:
                print("iterate: generated message")
            return message
        else:
            return None
