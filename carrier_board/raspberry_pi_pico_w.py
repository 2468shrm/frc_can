"""Support for the Team Appreciate Carrier Board for the Raspberry
Pi Pico W board.
"""

import board
import busio
import analogio
import digitalio

# For use with the Picobell CAN..
# from adafruit_mcp2515 import canio
from adafruit_mcp2515 import MCP2515 as CAN

# For use with the Ethernet FeatherWing socket..
# import adafruit_connection_manager
# import adafruit_requests
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K

# Board resources..
# I2C multiplexer IC
import adafruit_tca9548a

# PWM generators
import adafruit_pca9685
from adafruit_servokit import ServoKit

# For use with the MicroSD card socket..
import sdcardio
import storage

# For use with the NeoPixel interface..
import neopixel

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/2468shrm/frc_can.git"


class CarrierBoard:
    """CAN Carrier Board for Adafruit Feather M4 CAN Express board
    plus a slot for an Ethernet Feather Wing. The carrier board
    includes 4 DIOs with a level shifter and selectable 3.3V or
    5V supply, 4 buffered AINs (3.3V), and 3 STEMMA QT/Qwiic
    connectors. A NEOPIXEL status LED is also provided."""

    # board-level resources..

    # Pin definitions used for the two NEOPIXEL interfaces.
    # - A NEOPIXEL soldered to the carrier board and
    # - Another interface avaiable for a connected strip/ring/etc.
    # STATUS_NEO = board.GP17
    NEOPIXEL_IF = board.GP22

    # Pin definitions used for enabling/resetting/controlling some of
    # the board supporting ICs. They have biasing resistors on the PCB
    # to disable/hold in reset/enable, so they need to be pull high
    # in __init__()
    # Shared PWM generator output enable
    _PWM_OEN = board.GP12        # Pulled high by default, drive low to enable
    _MOTOR_OEN = board.GP28      # Pulled high by default, drive low to enable
    # I2C mux reset
    _MUX_RESETN = board.GP13     # need to pull high in __init__()
    # Level shifter for DIOs, output enable
    _LS_OE = board.GP14          # need to pull high in __init__()

    # Pin definitions used for the two analog input/ADC inputs.
    AI0 = board.A0
    AI1 = board.A1

    # Pin definitions used for the DIO interface.
    DIO0 = board.GP0
    DIO1 = board.GP1
    DIO2 = board.GP6
    DIO3 = board.GP7
    DIO4 = board.GP8
    DIO5 = board.GP9
    DIO6 = board.GP10
    DIO7 = board.GP11

    # SPI Pin definitions used for the Ethernet FeatherWing, Picobell
    # and microSD interfaces.
    _MISO = board.GP16
    _SCK = board.GP18
    _MOSI = board.GP19
    _ETHSPI_CS = board.GP15
    _CANSPI_CS = board.GP20
    _CANSPI_INT = board.GP21
    _MICRO_SD_CS = board.GP17

    # Pin definitions used for the I2C interfaces for the PWM generator IC.
    _PWM_SCL = board.GP5
    _PWM_SDA = board.GP4

    # Pin definitions used for the I2C interfaces for the I2C MUX.
    _I2CMUX_SCL = board.GP3
    _I2CMUX_SDA = board.GP2

    # I2C addresses for the PWM and Motor generator ICs
    _SERVO_PWM_GENERATOR_I2C_ADDR = 0x40
    _MOTOR_PWM_GENERATOR_I2C_ADDR = 0x41

    class StatusLED:

        PICO_W_LED = board.LED

        def __init__(self) -> None:
            # Initialize the LED on the Pico W board itself, turn it on and off
            self.pico_w_led = digitalio.DigitalInOut(self.PICO_W_LED)
            self.pico_w_led.direction = digitalio.Direction.OUTPUT
            self.pico_w_led.value = False

        def off(self) -> None:
            self.pico_w_led.value = False

        def on(self) -> None:
            self.pico_w_led.value = True

        def set_color(self, color) -> None:
            pass

    def __init__(self, configuration: dict) -> None:
        # Check to be sure there is a pico W plugged in..
        if board.board_id != "raspberry_pi_pico_w":
            raise RuntimeError(
                "expected to be running on a Raspberry Pi"
                " Pico W board"
            )

        self.config = configuration

        self.status = self.StatusLED()
        self.status.off()

        # Turn on the output enable pin of the level shifter
        self.ls_oe_pin = digitalio.DigitalInOut(self._LS_OE)
        self.ls_oe_pin.direction = digitalio.Direction.OUTPUT
        self.ls_oe_pin.value = False
        self.level_shifter_enabled = False

        # Per a note in some Adafruit docs, get the microSD cards running
        # before other SPI devices
        if "include_microsd" in self.config and \
                self.config["include_microsd"]:

            _mount_volumne_name = (
                self.config["include_microsd"]["mount_as"]
                if "mount_as" in self.config["include_microsd"]
                else "/sd"
            )

            # The microSD uses a SPI interface is across fixed pins on
            # the board
            _cs = digitalio.DigitalInOut(self.MICRO_SD_CS)
            _spi_bus = busio.SPI(self.SCK, MOSI=self.MOSI, MISO=self.MISO)

            # Now, create the sdcardio.SDCard instance in the carrier
            # board class
            self.microsd = sdcardio.SDCard(bus=_spi_bus, cs=_cs)

            self.vfs = storage.VfsFat(self.microsd)
            storage.mount(self.vfs, _mount_volumne_name)

        # configure CAN interface, it self.config enables it..
        if "include_can" in self.config and self.config["include_can"]:
            # Before creating the canio.CAN interace, check for optional
            # features
            self._loopback = (
                self.config["include_can"]["loopback"]
                if "loopback" in self.config["include_can"]
                else False
            )
            self._silent = (
                self.config["include_can"]["silent"]
                if "silent" in self.config["include_can"]
                else False
            )
            self._baudrate = (
                self.config["include_can"]["baudrate"]
                if "baudrate" in self.config["include_can"]
                else 1000000
            )
            self._auto_restart = (
                self.config["include_can"]["auto_restart"]
                if "auto_restart" in self.config["include_can"]
                else True
            )

            # Now, create the canio.CAN instance in the carrier board class
            _can_cs = digitalio.DigitalInOut(self._CANSPI_CS)
            _can_cs.switch_to_output()
            _spi = busio.SPI(self._SCK, self._MOSI, self._MISO)
            self.can = CAN(
                spi_bus=_spi,
                cs_pin=_can_cs,
                baudrate=self._baudrate,
                loopback=self._loopback,
                silent=self._silent,
                auto_restart=self._auto_restart,
            )

        # Configure Ethernet interface on the Ethernet Featherwing, if
        # self.config enables it
        if "include_eth" in self.config and self.config["include_eth"]:
            # The SPI interface is across fixed pins on the board
            _cs = digitalio.DigitalInOut(self.ETH_CS)
            _spi_bus = busio.SPI(self.SCK, MOSI=self.MOSI, MISO=self.MISO)

            # Before creating the WIZNET interace, check for optional features
            self._is_dhcp = (
                self.config["include_eth"]["is_dhcp"]
                if "is_dhcp" in self.config["include_eth"]
                else False
            )
            self._mac = (
                self.config["include_eth"]["mac"]
                if "mac" in self.config["include_eth"]
                else "DE:AD:BE:EF:FE:ED"
            )
            self._hostname = (
                self.config["include_eth"]["hostname"]
                if "hostname" in self.config["include_eth"]
                else None
            )
            self._debug = (
                self.config["include_eth"]["debug"]
                if "debug" in self.config["include_eth"]
                else False
            )

            # Now, create the WIZNET instance in the carrier board class
            self.eth = WIZNET5K(
                spi_bus=_spi_bus,
                cs=_cs,
                is_dhcp=self._is_dhcp,
                mac=self._mac,
                hostname=self._hostname,
                debug=self._debug,
            )

        if "include_i2c_mux" in self.config and \
                self.config["include_i2c_mux"]:
            # initialize the I2C mux
            # Pull I2C mux IC reset pin HIGH so that the mux is out of reset
            # and can be accessed
            self.mux_resetn = digitalio.DigitalInOut(self._MUX_RESETN)
            self.mux_resetn.direction = digitalio.Direction.OUTPUT
            self.mux_resetn.value = True

            self._mux_i2c = busio.I2C(self._I2CMUX_SCL, self._I2CMUX_SDA)
            self._i2cmux = adafruit_tca9548a.PCA9546A(self._mux_i2c)

            self.I2C0 = (
                self._i2cmux[0]
                if "init_i2c0" in self.config and self.config["init_i2c0"]
                else None
            )
            self.I2C1 = (
                self._i2cmux[1]
                if "init_i2c1" in self.config and self.config["init_i2c1"]
                else None
            )
            self.I2C2 = (
                self._i2cmux[2]
                if "init_i2c2" in self.config and self.config["init_i2c2"]
                else None
            )
            self.I2C3 = (
                self._i2cmux[3]
                if "init_i2c3" in self.config and self.config["init_i2c3"]
                else None
            )

        # Configure the analog in (ADC) interfaces, if self.config
        # enables it
        self.adc0 = (
            analogio.AnalogIn(self.AI0)
            if "init_ain0" in self.config and self.config["init_ain0"]
            else None
        )
        self.adc1 = (
            analogio.AnalogIn(self.AI1)
            if "init_ain1" in self.config and self.config["init_ain1"]
            else None
        )

        # initialize the DIO pins?
        self._enable_dio_level_shifters = False
        if "init_dio0" in self.config and self.config["init_dio0"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio0"] and
                    self.config["init_dio0"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio0"]["value"]
                if "value" in self.config["init_dio0"]
                else None
            )
            self.dio0 = digitalio.DigitalInOut(self.DIO0)
            self.dio0.direction = _direction
            if _value:
                self.dio0.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio0 = None

        if "init_dio1" in self.config and self.config["init_dio1"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio1"] and
                    self.config["init_dio1"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio1"]["value"]
                if "value" in self.config["init_dio1"]
                else None
            )
            self.dio1 = digitalio.DigitalInOut(self.DIO1)
            self.dio1.direction = _direction
            if _value:
                self.dio1.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio1 = None

        if "init_dio2" in self.config and self.config["init_dio2"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio2"] and
                    self.config["init_dio2"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio2"]["value"]
                if "value" in self.config["init_dio2"]
                else None
            )
            self.dio2 = digitalio.DigitalInOut(self.DIO2)
            self.dio2.direction = _direction
            if _value:
                self.dio2.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio2 = None

        if "init_dio3" in self.config and self.config["init_dio3"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio3"] and
                    self.config["init_dio3"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio3"]["value"]
                if "value" in self.config["init_dio3"]
                else None
            )
            self.dio3 = digitalio.DigitalInOut(self.DIO3)
            self.dio3.direction = _direction
            if _value:
                self.dio3.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio3 = None

        if "init_dio4" in self.config and self.config["init_dio4"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio4"] and
                    self.config["init_dio4"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio4"]["value"]
                if "value" in self.config["init_dio4"]
                else None
            )
            self.dio4 = digitalio.DigitalInOut(self.DIO4)
            self.dio4.direction = _direction
            if _value:
                self.dio4.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio4 = None

        if "init_dio5" in self.config and self.config["init_dio5"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio5"] and
                    self.config["init_dio5"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio5"]["value"]
                if "value" in self.config["init_dio5"]
                else None
            )
            self.dio5 = digitalio.DigitalInOut(self.DIO5)
            self.dio5.direction = _direction
            if _value:
                self.dio5.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio5 = None

        if "init_dio6" in self.config and self.config["init_dio6"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio6"] and
                    self.config["init_dio6"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio6"]["value"]
                if "value" in self.config["init_dio6"]
                else None
            )
            self.dio6 = digitalio.DigitalInOut(self.DIO6)
            self.dio6.direction = _direction
            if _value:
                self.dio6.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio6 = None

        if "init_dio7" in self.config and self.config["init_dio7"]:
            _direction = (
                digitalio.Direction.INPUT
                if ("as_input" in self.config["init_dio7"] and
                    self.config["init_dio7"]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _value = (
                self.config["init_dio7"]["value"]
                if "value" in self.config["init_dio7"]
                else None
            )
            self.dio7 = digitalio.DigitalInOut(self.DIO7)
            self.dio7.direction = _direction
            if _value:
                self.dio7.direction = _direction
            self._enable_dio_level_shifters = True
        else:
            self.dio7 = None

        # If any of the init_dioX are enable, turn on the level shifters
        if self._enable_dio_level_shifters:
            self.ls_oe_pin.value = True
            self.level_shifter_enabled = True

        if "include_pwm_generators" in self.config and \
                self.config["include_pwm_generators"]:
            print("Enabling PWM generator (PWM or Motor)")
            # PWM Generators
            # create an I2C busio instance with these two pins and then
            # create a PCA9685 instance
            self._pwm_i2c = busio.I2C(self._PWM_SCL, self._PWM_SDA)

            # Pull PWM generator IC output enable pin HIGH so that it will
            # not generate signals until enabled (LOW).
            self._pwm_oen = digitalio.DigitalInOut(self._PWM_OEN)
            self._pwm_oen.direction = digitalio.Direction.OUTPUT
            self._pwm_oen.value = True

            # Pull motor generator IC output enable pin HIGH so that it will
            # not generate signals until enabled (LOW).
            self._motor_oen = digitalio.DigitalInOut(self._MOTOR_OEN)
            self._motor_oen.direction = digitalio.Direction.OUTPUT
            self._motor_oen.value = True

            if (
                "enable_pwm_interface" in self.config["include_pwm_generators"]
                and self.config["include_pwm_generators"][
                    "enable_pwm_interface"
                ]
            ):
                self._pwm_oen.value = False
                print("Enabling PWM generator")
                self.pwm = ServoKit(
                    channels=8,
                    i2c=self._pwm_i2c,
                    address=self._SERVO_PWM_GENERATOR_I2C_ADDR
                )
                print("..done")

            if "enable_motor_interface" in self.config and \
                    self.config["enable_motor_interface"]:
                self._pwm_motor.value = False
                print("Enabling motor generator")
                print("..done")

        # Configure the neopixel interface on, if self.config
        # enables it
        if "init_neopixel" in self.config and self.config["init_neopixel"]:
            _num_pixels_on_board = (
                self.config["init_neopixel"]["num_pixels"]
                if "num_pixels" in self.config["init_neopixel"]
                else 1
            )
            self.neopixel = neopixel.NeoPixel(
                self.NEOPIXEL_IF,
                _num_pixels_on_board,
                brightness=0.3,
                auto_write=False
            )
            self.neopixel.fill(self.BLACK_COLOR)
            self.neopixel.show()

        self.status.on()

    def init_neopixel_strip(self, num_pixels_in_strip) -> None:
        self.num_pixels_in_strip = num_pixels_in_strip
        self.neopixel_strip = neopixel.NeoPixel(
            self.NEOPIXEL_STRIP,
            self.num_pixels_in_strip,
            brightness=0.2,
            auto_write=False
        )
        # fill with black/dark and show it
        self.neopixel_strip.fill((255, 0, 0))
        self.neopixel_strip.show()

    def reset_i2c_mux(self) -> None:
        self.mux_resetn = False
        # A delay here is likely good...
        self.mux_resetn = True

    def disable_pwm(self) -> None:
        self._pwm_oen.value = True

    def enable_pwm(self):
        self._pwm_oen.value = False

    def disable_motor(self) -> None:
        self._motor_oen.value = True

    def enable_motor(self) -> None:
        self._motor_oen.value = False

    def set_as_input(self, pin) -> None:
        digitalio.DigitalInOut(pin).direction = digitalio.Direction.INPUT

    def enable_level_shifter(self) -> None:
        self.ls_oe_pin.value = True
        self.level_shifter_enabled = True
