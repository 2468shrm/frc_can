
import time
import board
import canio
import struct
import neopixel

from frc_can import FRCCANDevice
from frc_can_handler import CANHandler
from can_carrier_board import CANCarrierBoard
from intake_sensor_2023 import INTAKE_SENSOR_2023

#
ccb = CANCarrierBoard()
i2c = ccb.I2C0()

# create an ToF object
dist_sensor = INTAKE_SENSOR_2023(i2c=i2c, filter=False, debug=True)

FILTER_ENABLE_MSG = FRCCANDevice(
            device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
            manufacturer=FRCCANDevice.MANUFACTURER_TEAM_USE,
            api=INTAKE_SENSOR_2023.INTAKE_SENSOR_2023_FILTER_ENABLE,
            device_number=1)
FILTER_DISABLE_MSG = FRCCANDevice(
            device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
            manufacturer=FRCCANDevice.MANUFACTURER_TEAM_USE,
            api=INTAKE_SENSOR_2023.INTAKE_SENSOR_2023_FILTER_DISABLE,
            device_number=1)

# Doesn't respond to any messages or RTRs, right now..
messageid_match_list = [
    canio.Match(id=FILTER_ENABLE_MSG.message_id, extended=True),
    canio.Match(id=FILTER_DISABLE_MSG.message_id, extended=True)
]

# A 100 ms period is just fine..
can_handler = CANHandler(matches=messageid_match_list, timeout=0.1)

can_handler.register_handler(FILTER_ENABLE_MSG.message_id, dist_sensor.filter_enable)
can_handler.register_handler(FILTER_DISABLE_MSG.message_id, dist_sensor.filter_disable)
can_handler.register_iteration(dist_sensor.iterate)

while True:
    can_handler.step()
