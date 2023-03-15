
import math
import struct
import time
import canio
import neopixel
import adafruit_vl53l4cd
from circular_buffer import CIRCULAR_BUFFER
from frc_can import FRCCANDevice
from can_carrier_board import CANCarrierBoard
from led_string import LED_STRING


class INTAKE_DUAL_SENSOR_2023:
    INTAKE_SENSOR_2023_DISTANCE = 1
    INTAKE_SENSOR_2023_FILTER_ENABLE = 2
    INTAKE_SENSOR_2023_FILTER_DISABLE = 3

    STATE_OBJECT_NOT_DETECTED = 0
    STATE_OBJECT_DETECTED = 2

    OBJECT_THRESHOLD = 25.0

    def __init__(self, i2c0, i2c1, device_number=1,
                 filter=False, debug=False, do_calibrate=False,
                 real_sensor_distance=0, left_sensor_distance=0,
                 right_sensor_distance=0):
        self.distance_message = FRCCANDevice(
            device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
            manufacturer=FRCCANDevice.MANUFACTURER_TEAM_USE,
            api=self.INTAKE_SENSOR_2023_DISTANCE,
            device_number=device_number)

        self.debug = debug
        self.filter = filter
        self.do_calibrate = do_calibrate

        if self.debug:
            print("__init__")
        if real_sensor_distance == 0:
            if self.debug:
                print("parameter real_sensor_distance must be specified")
            return None
        self.real_sensor_distance = real_sensor_distance

        if self.debug:
            print("initializing I2C0 interface")
        self.i2c0 = i2c0
        self.vl53_0 = adafruit_vl53l4cd.VL53L4CD(self.i2c0)

        # OPTIONAL: can set non-default values
        self.vl53_0.inter_measurement = 0
        self.vl53_0.timing_budget = 200

        if self.debug:
            print("VL53L4CD #0")
            print("--------------------")
            model_id, module_type = self.vl53_0.model_info
            print("Model ID: 0x{:0X}".format(model_id))
            print("Module Type: 0x{:0X}".format(module_type))
            print("Timing Budget: {}".format(self.vl53_0.timing_budget))
            print("Inter-Measurement: {}".format(self.vl53_0.inter_measurement))
            print("--------------------")
            print("MessageID {:08x}".format(self.distance_message.message_id))
            print("--------------------")

        self.vl53_0.start_ranging()

        while not self.vl53_0.data_ready:
            pass
        self.vl53_0.clear_interrupt()
        if self.vl53_0.distance > self.OBJECT_THRESHOLD:
            self.state = self.STATE_OBJECT_NOT_DETECTED
        else:
            self.state = self.STATE_OBJECT_DETECTED

        if self.debug:
            print("initializing I2C1 interface")
        self.i2c1 = i2c1
        self.vl53_1 = adafruit_vl53l4cd.VL53L4CD(i2c1)
        self.vl53_1.inter_measurement = 0
        self.vl53_1.timing_budget = 200

        if self.debug:
            print("VL53L4CD #1")
            print("--------------------")
            model_id, module_type = self.vl53_1.model_info
            print("Model ID: 0x{:0X}".format(model_id))
            print("Module Type: 0x{:0X}".format(module_type))
            print("Timing Budget: {}".format(self.vl53_1.timing_budget))
            print("Inter-Measurement: {}".format(self.vl53_1.inter_measurement))

        self.vl53_1.start_ranging()

        self.led_string = LED_STRING(led_pixels_per_m=60,
                                     sensor=self)

        if self.do_calibrate:
            self.calibrate()
        else:
            if left_sensor_distance > 0:
                self.left_distance_max = left_sensor_distance
            else:
                self.left_distance_max = real_sensor_distance - 2.0
            if right_sensor_distance > 0:
                self.right_distance_max = right_sensor_distance
            else:
                self.right_distance_max = real_sensor_distance - 2.0

    # ---------------------------------------
    def calibrate(self):
        if self.debug:
            print("calibrate()")
        self.led_string.calibrating()
        _samples = 20
        if self.debug:
            print(" Calibrating VL53L4CD #0")
        sensor_data_0 = CIRCULAR_BUFFER(5)
        for i in range(_samples):
            while not self.vl53_0.data_ready:
                pass
            self.vl53_0.clear_interrupt()
            _distance = self.vl53_0.distance
            if self.debug:
                print(f" +++ {_distance}")
            sensor_data_0.add(_distance)
        _left_distance_avg = sensor_data_0.average()
        if self.debug:
            print(f" ..sees width: {_left_distance_avg}")
        self.left_distance_max = _left_distance_avg - 2.0

        if self.debug:
            print(" Calibrating VL53L4CD #1")
        sensor_data_1 = CIRCULAR_BUFFER(5)
        for i in range(_samples):
            while not self.vl53_1.data_ready:
                pass
            self.vl53_1.clear_interrupt()
            _distance = self.vl53_1.distance
            if self.debug:
                print(f" +++ {_distance}")
            sensor_data_1.add(_distance)
        _right_distance_avg = sensor_data_1.average()
        if self.debug:
            print(f" ..sees width: {_right_distance_avg}")
        self.right_distance_max = _right_distance_avg - 2.0

    # ---------------------------------------
    def filter_enable(self, message):
        if self.debug:
            print("filter_enable")
        self.filter = True

    # ---------------------------------------
    def filter_disable(self, message):
        if self.debug:
            print("filter_disable")
        self.filter = False

    # ---------------------------------------
    def detect(self):
        if self.debug:
            print("detect")
        _left_normalized = (self.left_distance / self.left_distance_max) * \
            self.real_sensor_distance
        _right_normalized = (self.right_distance / self.right_distance_max) * \
            self.real_sensor_distance

        _width = self.real_sensor_distance - \
            (_left_normalized + _right_normalized)
        _center = _left_normalized + (_width/2)
        if self.debug:
            print(f"center: {_center}, width: {_width}")
        return _center, _width

    # ---------------------------------------
    def iterate(self):
        if self.debug:
            print("iterate")

        # wait for a reading from both sides
        while not self.vl53_0.data_ready:
            pass
        self.vl53_0.clear_interrupt()
        while not self.vl53_1.data_ready:
            pass
        self.vl53_1.clear_interrupt()

        if self.debug:
            print("update")
        # the following are relative to the total width..
        self.left_distance = self.vl53_0.distance
        self.right_distance = self.vl53_1.distance

        # This is where we should filter.. and keep state.
        # Two states: OBJECT_CAPTURED, OBJECT_MISSING
        # if missing and 2 samples with distance < X goto OBJECT_CAPTURED
        #    and send message
        # if captured and 2 samples with deistance > X goto OBJECT_missing
        #    and send message
        if self.filter:
            _send_message = False
            if self.state > self.STATE_OBJECT_NOT_DETECTED:
                if self.left_distance > self.OBJECT_THRESHOLD:
                    self.state -= 1
                    if self.state == self.STATE_OBJECT_NOT_DETECTED:
                        _send_message = True
            else:
                if self.left_distance <= self.OBJECT_THRESHOLD:
                    self.state += 1
                    if self.state == self.STATE_OBJECT_DETECTED:
                        _send_message = True
        else:
            _send_message = True

        if (self.left_distance > self.left_distance_max) and \
           (self.right_distance > self.right_distance_max):
            if self.debug:
                print("..not detected")
            self.led_string.not_detected()
            return
        else:
            if self.debug:
                print("..detected")
            _center, _width = self.detect()
            self.led_string.detected()

        if _send_message:
            msg_body = struct.pack("@ff", _center, _width)
            message = canio.Message(id=self.distance_message.message_id,
                                    data=msg_body,
                                    extended=True)
            if self.debug:
                print("iterate: generated message")
            return message
        else:
            return None
