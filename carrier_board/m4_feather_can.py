"""Support for the Team Appreciate Carrier Board for the Adafruit
Feather M4 CAN board.
"""

import board
import busio
import analogio
import digitalio

# For use with the M4 Feather CAN Express's built-in CAN..
from canio import CAN
# from canio import BusState, Message, RemoteTransmissionRequest

# For use with the Ethernet FeatherWing socket..
# import adafruit_connection_manager
# import adafruit_requests
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K

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

    # Neopixel interface
    NEOPIXEL_IF = board.D4

    # Level shifter for DIOs, output enable
    _LS_OE = board.A5

    # Pin definitions used for the FOUR analog input/ADC inputs.
    AI0 = board.A0
    AI1 = board.A1
    AI2 = board.A2
    AI3 = board.A3

    # Pin definitions used for the DIO interface.
    DIO0 = board.D10
    DIO1 = board.D9
    DIO2 = board.D6
    DIO3 = board.D11

    # I2C / STEMMA QT / Qwiic connections
    SCL0 = board.SCL
    SDA0 = board.SDA

    SCL1 = board.D0
    SDA1 = board.D1

    SCL2 = board.D13
    SDA2 = board.D12

    # SPI Pin definitions used for the Ethernet FeatherWing and microSD
    # interfaces.
    _MISO = board.MISO
    _MOSI = board.MOSI
    _SCK = board.SCK
    _ETHSPI_CS = board.D5
    _MICRO_SD_CS = board.A4

    class StatusLED:
        OFF = (0, 0, 0)  # Black
        GREEN = (0, 255, 0)  # Green

        # The feather board has a neopixel for status too..
        STATUS_NEO = board.NEOPIXEL

        def __init__(self) -> None:
            # Configure the neopixel status interface on the Feather board
            _num_pixels_on_board = 1
            self.neopixel_status = neopixel.NeoPixel(
                self.STATUS_NEO,
                _num_pixels_on_board,
                brightness=0.3,
                auto_write=False
            )

        def off(self) -> None:
            self.set_color(self.OFF)

        def on(self, color=GREEN) -> None:
            self.set_color(color)

        def set_color(self, color) -> None:
            self.neopixel_status.fill(color)
            self.neopixel_status.show()

    def __init__(self, configuration: dict) -> None:
        # make sure running on a Feather M4 CAN, if not complain
        if board.board_id != "feather_m4_can":
            raise RuntimeError(
                "expected to be running on a Feather M4 CAN board"
            )

        self.config = configuration
        self.status = self.StatusLED()
        self.status.off()

        # Turn on the output enable pin of the level shifter
        self.ls_oe_pin = digitalio.DigitalInOut(self._LS_OE)
        self.ls_oe_pin.direction = digitalio.Direction.OUTPUT
        self.ls_oe_pin.value = False
        self.level_shifter_enabled = False

        # configure CAN interface, it self.config enables it..
        if "include_can" in self.config and self.config["include_can"]:
            # Before creating the canio.CAN interace, check for optional
            # features
            _loopback = (
                self.config["include_can"]["loopback"]
                if "loopback" in self.config["include_can"]
                else False
            )

            _silent = (
                self.config["include_can"]["silent"]
                if "silent" in self.config["include_can"]
                else False
            )

            _baudrate = (
                self.config["include_can"]["baudrate"]
                if "baudrate" in self.config["include_can"]
                else 1000000
            )

            _auto_restart = (
                self.config["include_can"]["auto_restart"]
                if "auto_restart" in self.config["include_can"]
                else True
            )

            _listener_match_list = (
                self.config["include_can"]["listener_match_list"]
                if "listener_match_list" in self.config["include_can"]
                else None
            )

            _timeout = (
                self.config["include_can"]["timeout"]
                if "timeout" in self.config["include_can"]
                else 0.1
            )

            # Before creating the canio.CAN instance, power up the transceiover
            # If the CAN transceiver has a standby pin, bring it out of standby
            # mode
            if hasattr(board, "CAN_STANDBY"):
                _standby = digitalio.DigitalInOut(board.CAN_STANDBY)
                _standby.switch_to_output(False)

            # If the CAN transceiver is powered by a boost converter, turn on
            # its supply
            if hasattr(board, "BOOST_ENABLE"):
                _boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
                _boost_enable.switch_to_output(True)

            # Now, create the canio.CAN instance in the carrier board class
            self.can = CAN(
                rx=board.CAN_RX,
                tx=board.CAN_TX,
                baudrate=_baudrate,
                loopback=_loopback,
                silent=self._silent,
                auto_restart=self._auto_restart,
            )

            self.listener = self.can.listener(
                matches=self._listener_match_list,
                timeout=_timeout
            )

        # Create busio instances for I2C0-I2C2
        if "init_i2c0" in self.config and self.config["init_i2c0"]:
            self.I2C0 = busio.I2C(self.SCL0, self.SDA0)
        if "init_i2c1" in self.config and self.config["init_i2c1"]:
            self.I2C1 = busio.I2C(self.SCL1, self.SDA1)
        if "init_i2c2" in self.config and self.config["init_i2c2"]:
            self.I2C2 = busio.I2C(self.SCL2, self.SDA2)

        # Configure Ethernet interface on the Ethernet Featherwing, if
        # self.config enables it
        if "include_eth" in self.config and self.config["include_eth"]:
            # The SPI interface is across fixed pins on the board
            _cs = digitalio.DigitalInOut(self._ETHSPI_CS)
            _spi_bus = busio.SPI(self._SCK, MOSI=self._MOSI, MISO=self._MISO)

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

        if "include_microsd" in self.config and \
                self.config["include_microsd"]:

            _mount_volumne_name = (
                self.config["include_microsd"]["mount_as"]
                if "mount_as" in self.config["include_microsd"]
                else "/sd"
            )

            # The microSD uses a SPI interface is across fixed pins on
            # the board
            _spi_bus = busio.SPI(self._SCK, MOSI=self._MOSI, MISO=self._MISO)

            # Now, create the sdcardio.SDCard instance in the carrier board
            # class
            self.microsd = sdcardio.SDCard(spi=_spi_bus, cs=self._MICRO_SD_CS)

            self.vfs = storage.VfsFat(self.microsd)
            storage.mount(self.vfs, _mount_volumne_name)

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

        # If any of the init_dioX are enable, turn on the level shifters
        if self._enable_dio_level_shifters:
            self.enable_level_shifter()

        # Configure the analog in (ADC) interfaces, if self.config
        # enables it
        if "init_ain0" in self.config and self.config["init_ain0"]:
            self.adc0 = analogio.AnalogIn(self.AI0)
        if "init_ain1" in self.config and self.config["init_ain1"]:
            self.adc1 = analogio.AnalogIn(self.AI1)
        if "init_ain2" in self.config and self.config["init_ain2"]:
            self.adc2 = analogio.AnalogIn(self.AI2)
        if "init_ain3" in self.config and self.config["init_ain3"]:
            self.adc3 = analogio.AnalogIn(self.AI3)

        # Configure the neopixel interface on, if self.config
        # enables it
        if "init_neopixel" in self.config and self.config["init_neopixel"]:
            _num_pixels_on_board = (
                "num_pixels" in self.config["init_neopixel"]
                if self.config["init_neopixel"]["num_pixels"]
                else 1
            )
            self.neopixel = neopixel.NeoPixel(
                self.NEOPIXEL_IF,
                _num_pixels_on_board,
                brightness=0.3,
                auto_write=False
            )
            self.neopixel.fill((0, 0, 0))
            self.neopixel.show()

        self.status.on()

    def enable_level_shifter(self) -> None:
        self.ls_oe_pin.value = True
        self.level_shifter_enabled = True
