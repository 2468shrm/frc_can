"""Support for the Team Appreciate Carrier Board for the Adafruit
Feather M4 CAN board.
"""

import board
import busio
import digitalio


class CANCarrierBoard:
    NEOPIXEL = board.D4

    DIO0 = board.D6
    DIO1 = board.D9
    DIO2 = board.D10
    DIO3 = board.D11

    AI0 = board.A0
    AI1 = board.A1
    AI2 = board.A2
    AI3 = board.A3

    SCL0 = board.SCL
    SDA0 = board.SDA

    SCL1 = board.D0
    SDA1 = board.D1

    SCL2 = board.SCK
    SDA2 = board.D5

    SCL3 = board.D13
    SDA3 = board.D12

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

        if enable_dio_pull_ups:
            """Either board, conditionally pre-enable DIO pull ups"""
            self.enable_dio_pullups()

        if self.is_v2_carrier:
            """V2 board. The A5 pin is used for the OE of the level shifter
            which needs to be declared and declared as an output.
            Howecer, the level shifter is not enabled. It is enabled
            by calling enable_level_shifter()."""
            self.LS_OE = board.A5
            self.ls_oe_pin = digitalio.DigitalInOut(self.LS_OE)
            self.ls_oe_pin.direction = digitalio.Direction.OUTPUT
            self.ls_oe_pin.value = False
            self.level_shifter_enabled = False

    def I2C0(self):
        return busio.I2C(CANCarrierBoard.SCL0, CANCarrierBoard.SDA0)

    def I2C1(self):
        return busio.I2C(CANCarrierBoard.SCL1, CANCarrierBoard.SDA1)

    def I2C2(self):
        return busio.I2C(CANCarrierBoard.SCL2, CANCarrierBoard.SDA2)

    def I2C3(self):
        return busio.I2C(CANCarrierBoard.SCL3, CANCarrierBoard.SDA3)

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
        self.enable_dio_pullup(CANCarrierBoard.DIO0)
        self.enable_dio_pullup(CANCarrierBoard.DIO1)
        self.enable_dio_pullup(CANCarrierBoard.DIO2)
        self.enable_dio_pullup(CANCarrierBoard.DIO3)

    def set_as_input(self, pin):
        digitalio.DigitalInOut(pin).direction = digitalio.Direction.INPUT
