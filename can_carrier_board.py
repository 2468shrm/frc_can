"""Support for the Team Appreciate Carrier Board for the Adafruit Feather M4 CAN board.
"""
# from can_carrier_board import CANCarrierBoard


import board
import digitalio

class CANCarrierBoard:
    def __init__(self, v2=False):
        """I/Os allocated for use with the Team Appreciate CAN Carrier Board."""

        # make sure running on a Feather M4 CAN
        if board.board_id != "feather_m4_can":
            raise RuntimeError("expected to be running on a Feather M4 CAN board")
        self.NEOPIXEL = board.D4

        self.DIO0 = board.D6
        self.DIO1 = board.D9
        self.DIO2 = board.D10
        self.DIO3 = board.D11

        self.AI0 = board.A0
        self.AI1 = board.A1
        self.AI2 = board.A2
        self.AI3 = board.A3

        self.SCL0 = board.SCL
        self.SDA0 = board.SDA

        self.SCL1 = board.D0
        self.SDA1 = board.D1

        self.SCL2 = board.SCK
        self.SDA2 = board.D5

        self.SCL3 = board.D13
        self.SDA3 = board.D12

        """V2 board, the A2 pin is used for the OE of the level shifter"""
        if v2:
            ls_oe = digitalio.DigitalInOut(board.A2)
            ls_oe.direction = digitalio.Direction.OUTPUT
            ls_oe.value = True
