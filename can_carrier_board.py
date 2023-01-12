"""Support for the Team Appreciate Carrier Board for the Adafruit
Feather M4 CAN board.
"""

import board
import digitalio


class CANCarrierBoard:
    def __init__(self, v2=False, enable_level_shifter=False,
                 enable_dio_pull_ups=False):
        """I/Os allocated for use with the Team Appreciate CAN
        Carrier Board."""

        self.is_v2_carrier = v2
        self.level_shifter_enabled = False
        self.dio_pull_ups_enabled = False

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

        if enable_dio_pull_ups:
            """Either board, conditionally pre-enable DIO pull ups"""
            self.enable_dio_pullups()

        if self.is_v2_carrier:
            """V2 board, the A5 pin is used for the OE of the level shifter"""
            self.LS_OE = board.A5
            self.ls_oe_pin = digitalio.DigitalInOut(self.LS_OE)
            self.ls_oe_pin.direction = digitalio.Direction.OUTPUT

    def enable_level_shifter(self):
        if self.is_v2_carrier:
            self.ls_oe_pin.value = True
            self.level_shifter_enabled = True

    def disable_level_shifter(self):
        if self.is_v2_carrier:
            self.ls_oe_pin.value = False
            self.level_shifter_enabled = False

    def enable_dio_pullup(self, pin):
        digitalio.DigitalInOut(pin).pull = digitalio.Pull.UP

    def enable_all_dio_pullups(self):
        self.enable_dio_pullup(self.DIO0)
        self.enable_dio_pullup(self.DIO1)
        self.enable_dio_pullup(self.DIO2)
        self.enable_dio_pullup(self.DIO3)

    def set_as_input(self, pin):
        digitalio.DigitalInOut(pin).direction = digitalio.Direction.INPUT
