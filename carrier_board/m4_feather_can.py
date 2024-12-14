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
    DIO0 = board.D6
    DIO1 = board.D9
    DIO2 = board.D10
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

    def __init__(self, configuration: dict = {}) -> None:
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

        #
        if "init_microsd" in self.config and self.config["init_microsd"]:
            self.init_microsd()
        else:
            self.microsd = None

        # configure CAN interface, it self.config enables it..
        if "init_can" in self.config and self.config["init_can"]:
            self.init_can()
        else:
            self.can = None

        # Create busio instances for I2C0-I2C2
        if "init_i2c0" in self.config and self.config["init_i2c0"]:
            self.i2c0 = busio.I2C(self.SCL0, self.SDA0)
        if "init_i2c1" in self.config and self.config["init_i2c1"]:
            self.i2c1 = busio.I2C(self.SCL1, self.SDA1)
        if "init_i2c2" in self.config and self.config["init_i2c2"]:
            self.i2c2 = busio.I2C(self.SCL2, self.SDA2)

        # Configure Ethernet interface on the Ethernet Featherwing, if
        # self.config enables it
        if "init_eth" in self.config and self.config["init_eth"]:
            self.init_eth()
        else:
            self.eth = None

        # initialize the DIO pins based on config dict contents
        self._enable_dio_level_shifters = False
        self.dio0 = self.init_dio("init_dio0", self.DIO0)
        self.dio1 = self.init_dio("init_dio1", self.DIO1)
        self.dio2 = self.init_dio("init_dio2", self.DIO2)
        self.dio3 = self.init_dio("init_dio3", self.DIO3)

        # If any of the init_dioX are enable, turn on the level shifters
        if self._enable_dio_level_shifters:
            self.enable_level_shifter()

        # Configure the analog in (ADC) interfaces, if self.config
        # enables it
        if "init_ain0" in self.config and self.config["init_ain0"]:
            self.ain0 = analogio.AnalogIn(self.AI0)
        if "init_ain1" in self.config and self.config["init_ain1"]:
            self.ain1 = analogio.AnalogIn(self.AI1)
        if "init_ain2" in self.config and self.config["init_ain2"]:
            self.ain2 = analogio.AnalogIn(self.AI2)
        if "init_ain3" in self.config and self.config["init_ain3"]:
            self.ain3 = analogio.AnalogIn(self.AI3)

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
            self.neopixel.fill((0, 0, 0))
            self.neopixel.show()

        self.status.on()

    def disable_level_shifter(self) -> None:
        self.ls_oe_pin.value = False
        self.level_shifter_enabled = False

    def enable_level_shifter(self, init_dios=False) -> None:
        """The digital signal connected to the level shifter output
        enable is driven high so that the level shifter connects
        header pin to M4 I/O.
        :param bool init_dios: if True the four DIOs are configured.
        :type priority: integer or None
        :return: None
        """
        self.ls_oe_pin.value = True
        self.level_shifter_enabled = True

        # Initalize the DIOs
        if init_dios:
            if self.dio0 is None:
                self.dio0 = self.init_dio("init_dio0", self.DIO0)
            if self.dio1 is None:
                self.dio1 = self.init_dio("init_dio1", self.DIO1)
            if self.dio2 is None:
                self.dio2 = self.init_dio("init_dio2", self.DIO2)
            if self.dio3 is None:
                self.dio3 = self.init_dio("init_dio3", self.DIO3)

    def init_dio(self, keyname, pin):
        if keyname in self.config and self.config[keyname]:
            _set_direction = "as_input" in self.config[keyname]
            _direction = (
                digitalio.Direction.INPUT
                if (_set_direction and
                    self.config[keyname]["as_input"])
                else digitalio.Direction.OUTPUT
            )
            _pullup = (
                ("pullup" in self.config[keyname]) and (
                        _set_direction and self.config[keyname]["as_input"]
                    )
            )
            _set_value = "value" in self.config[keyname]
            _value = (
                self.config[keyname]["value"]
                if _set_value
                else None
            )
            _pin = digitalio.DigitalInOut(pin)
            if _set_direction:
                _pin.direction = _direction
            if _pullup:
                _pin.pull = digitalio.Pull.UP
            if _set_value:
                _pin.value = _value
            self._enable_dio_level_shifters = True
        else:
            _pin = None
        return _pin

    def init_can(self):
        # Before creating the canio.CAN interace, check for optional
        # features
        _loopback = (
            self.config["init_can"]["loopback"]
            if "loopback" in self.config["init_can"]
            else False
        )

        _silent = (
            self.config["init_can"]["silent"]
            if "silent" in self.config["init_can"]
            else False
        )

        _baudrate = (
            self.config["init_can"]["baudrate"]
            if "baudrate" in self.config["init_can"]
            else 1000000
        )

        _auto_restart = (
            self.config["init_can"]["auto_restart"]
            if "auto_restart" in self.config["init_can"]
            else True
        )

        _has_listener_match_list = (
            "listener_match_list" in self.config["init_can"]
        )

        _listener_match_list = (
            self.config["init_can"]["listener_match_list"]
            if _has_listener_match_list
            else None
        )

        _timeout = (
            self.config["init_can"]["timeout"]
            if "timeout" in self.config["init_can"]
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

        print(f"INFO: Starting canio.CAN with: {_baudrate=} {_loopback=}" +
              f" {_silent=} {_auto_restart=}")
        # Now, create the canio.CAN instance in the carrier board class
        self.can = CAN(
            rx=board.CAN_RX,
            tx=board.CAN_TX,
            baudrate=_baudrate,
            loopback=_loopback,
            silent=_silent,
            auto_restart=_auto_restart,
        )

        print(f"INFO: Starting canio.CAN.listener with" +
              f" {_has_listener_match_list=}" +
              f" {_listener_match_list=} {_timeout=}")
        # Create a listener, using the match list constructed in the config
        if _has_listener_match_list:
            self.listener = self.can.listen(
                matches=_listener_match_list,
                timeout=_timeout
            )
        else:
            self.listener = self.can.listen(timeout=_timeout)

    def init_eth(self):
        # The SPI interface is across fixed pins on the board
        _cs = digitalio.DigitalInOut(self._ETHSPI_CS)
        _spi_bus = busio.SPI(self._SCK, MOSI=self._MOSI, MISO=self._MISO)

        # Before creating the WIZNET interace, check for optional features
        _is_dhcp = (
            self.config["init_eth"]["is_dhcp"]
            if "is_dhcp" in self.config["init_eth"]
            else False
        )

        _mac = (
            self.config["init_eth"]["mac"]
            if "mac" in self.config["init_eth"]
            else "DE:AD:BE:EF:FE:ED"
        )

        _hostname = (
            self.config["init_eth"]["hostname"]
            if "hostname" in self.config["init_eth"]
            else None
        )

        _debug = (
            self.config["init_eth"]["debug"]
            if "debug" in self.config["init_eth"]
            else False
        )

        _if_config = (
            self.condif["init_eth"]["if_condig"]
            if "if_config" in self.config["init_eth"]
            else False
        )

        # Now, create the WIZNET instance in the carrier board class
        self.eth = WIZNET5K(
            spi_bus=_spi_bus,
            cs=_cs,
            is_dhcp=_is_dhcp,
            mac=_mac,
            hostname=_hostname,
            debug=_debug,
        )

        # Emply a manual interface configuration if we set is_dhcp to false and
        # if_config is set to a tuple containing:
        #   (IP_ADDRESS, SUBNET_MASK, GATEWAY_ADDRESS, DNS_SERVER)
        if not _is_dhcp and _if_config:
            self.eth.ifconfig = _if_config

    def init_microsd(self):
        _mount_volumne_name = (
            self.config["init_microsd"]["mount_as"]
            if "mount_as" in self.config["init_microsd"]
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
