"""Support for the Team Appreciate Carrier Board for the Adafruit
Feather M4 CAN board.
"""

import board
import digitalio


class CANCarrierBoard:
    def __init__(self, v2=False, dio_pull_ups=False):
        """I/Os allocated for use with the Team Appreciate CAN
        Carrier Board."""

        # make sure running on a Feather M4 CAN
        if board.board_id != "feather_m4_can":
            raise RuntimeError("expected to be running on a Feather"
                               "M4 CAN board")
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

        if dio_pull_ups:
            """Either board, conditionally pre-enable DIO pull ups"""
            dio0 = digitalio.DigitalInOut(self.DIO0)
            dio0.pull = digitalio.Pull.UP
            dio0.direction = digitalio.Direction.INPUT

            dio1 = digitalio.DigitalInOut(self.DIO1)
            dio1.pull = digitalio.Pull.UP
            dio1.direction = digitalio.Direction.INPUT

            dio2 = digitalio.DigitalInOut(self.DIO2)
            dio2.pull = digitalio.Pull.UP
            dio2.direction = digitalio.Direction.INPUT

            dio3 = digitalio.DigitalInOut(self.DIO3)
            dio3.pull = digitalio.Pull.UP
            dio3.direction = digitalio.Direction.INPUT

        if v2:
            """V2 board, the A5 pin is used for the OE of the level shifter"""
            self.LS_OE = board.A5
            ls_oe = digitalio.DigitalInOut(self.LS_OE)
            ls_oe.direction = digitalio.Direction.OUTPUT
            ls_oe.value = True
