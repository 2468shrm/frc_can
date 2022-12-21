
import time
import board
import canio
import struct
import neopixel


# from softencoder import SoftEncoder
from frc_can import FRCCANDevice
from frc_can_handler import CANHandler
from can_carrier_board import CANCarrierBoard
from robot_signal_light import RSL


# create an RSL object
rsl = RSL(pin=CANCarrierBoard.NEOPIXEL, num_pixels=16)

# Messages to listen to.. are heartbeat messages sent by the roboRIO
# WPILib heartbeat message ID (see
# https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html)
HEARTBEAT = FRCCANDevice()
HEARTBEAT.update(0x01011840)

messageid_match_list = [canio.Match(id=HEARTBEAT.message_id, extended=True)]

can_handler = CANHandler(matches=messageid_match_list, timeout=0.01)
can_handler.register_handler(message_id=HEARTBEAT.message_id, function=rsl.can_heartbeat_message)
can_handler.register_iteration(rsl.iterate)

while True:
    can_handler.step()
