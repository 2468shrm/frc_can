"""Support for the Team Appreciate Carrier Board for the Adafruit
Feather M4 CAN board.
"""

import board
import busio
import digitalio

# For use with the M4 Feather CAN Express's built-in CAN..
from canio import Message, RemoteTransmissionRequest
from canio import CAN, BusState

# For optional use with the Ethernet FeatherWing board
#import adafruit_connection_manager
#import adafruit_requests
#from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
#import neopixel

# For optional use with a microSD card
#import sdcardio
#import storage

class CarrierBoard:
    """CAN Carrier Board for Adafruit Feather M4 CAN Express board
       plus a slot for an Ethernet Feather Wing. The carrier board
       includes 4 DIOs with a level shifter and selectable 3.3V or
       5V supply, 4 buffered AINs (3.3V), and 3 STEMMA QT/Qwiic
       connectors. A NEOPIXEL status LED is also provided.
    """
    # The feather board has a neopixel for status too.. 
    STATUS_NEO = board.NEOPIXEL

    # Neopixel interface
    NEOPIXEL_IF = board.D4

    # Digital inputs
    DIO0 = board.D6
    DIO1 = board.D9
    DIO2 = board.D10
    DIO3 = board.D11

    # Buffered AIN
    AI0 = board.A0
    AI1 = board.A1
    AI2 = board.A2
    AI3 = board.A3

    # I2C / STEMMA QT / Qwiic connections
    SCL0 = board.SCL
    SDA0 = board.SDA

    SCL1 = board.D0
    SDA1 = board.D1

    SCL2 = board.D13
    SDA2 = board.D12

    # SPI definitions
    SCK = board.SCK
    MOSI = board.MOSI
    MISO = board.MISO

    # CHIP Selects for the SPI..
    ETH_CS = board.D5
    MICRO_SD_CS = board.A4

    # Level shifter for DIOs, output enable
    _LS_OE = board.A5

    # STATUS_NEO encodings
    BOOT_START_COLOR = (255,0,0)  # Red
    BOOT_READY_COLOR = (0,255,0)  # Green
    BLACK_COLOR = (0,0,0)         # Black

    def __init__(self, configuration: dict) -> CarrierBoard:
        # make sure running on a Feather M4 CAN, if not complain
        if board.board_id != "feather_m4_can":
            raise RuntimeError("expected to be running on a Feather"
                               "M4 CAN board")

        # Configure the neopixel status interface on the Feather board
        import neopixel
        _num_pixels_on_board = 1
        self.neopixel_status = neopixel.NeoPixel(self.STATUS_NEO,
                                                 _num_pixels_on_board,
                                                 brightness=0.3, auto_write=False)
        self.neopixel_status.fill(self.BOOT_START_COLOR)
        self.neopixel_status.show()

        # Turn on the output enable pin of the level shifter
        self.ls_oe_pin = digitalio.DigitalInOut(self._LS_OE)
        self.ls_oe_pin.direction = digitalio.Direction.OUTPUT
        self.ls_oe_pin.value = False
        self.level_shifter_enabled = False

        # configure CAN interface, it configuration enables it..
        if "include_can" in configuration and configuration["include_can"]:
            # Before creating the canio.CAN interace, check for optional features
            self._loopback = configuration["include_can"]["loopback"] \
                if "loopback" in configuration["include_can"] else False
            self._silent = configuration["include_can"]["silent"] \
                if "silent" in configuration["include_can"] else False
            self._baudrate = configuration["include_can"]["baudrate"] \
                if "baudrate" in configuration["include_can"] else 1000000
            self._auto_restart = configuration["include_can"]["auto_restart"] \
                if "auto_restart" in configuration["include_can"] else True
            
            # Before creating the canio.CAN instance, power up the transceiover
            # If the CAN transceiver has a standby pin, bring it out of standby mode
            if hasattr(board, 'CAN_STANDBY'):
                _standby = digitalio.DigitalInOut(board.CAN_STANDBY)
                _standby.switch_to_output(False)

            # If the CAN transceiver is powered by a boost converter, turn on its supply
            if hasattr(board, 'BOOST_ENABLE'):
                _boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
                _boost_enable.switch_to_output(True)

            # Now, create the canio.CAN instance in the carrier board class
            self.can = CAN(rx=board.CAN_RX, tx=board.CAN_TX,
                           baudrate=self._baudrate, loopback=self._loopback,
                           silent=self._silent, auto_restart=self._auto_restart)

        # Configure Ethernet interface on the Ethernet Featherwing, if configuration
        # enables it
        if "include_eth" in configuration and configuration["include_eth"]:
            # The SPI interface is across fixed pins on the board
            _cs = digitalio.DigitalInOut(self.ETH_CS)
            _spi_bus = busio.SPI(self.SCK, MOSI=self.MOSI, MISO=self.MISO)

            # Before creating the WIZNET interace, check for optional features
            self._is_dhcp = configuration["include_eth"]["is_dhcp"] \
                if "is_dhcp" in configuration["include_eth"] else False
            self._mac = configuration["include_eth"]["mac"] \
                if "mac" in configuration["include_eth"] else 'DE:AD:BE:EF:FE:ED'
            self._hostname = configuration["include_eth"]["hostname"] \
                if "hostname" in configuration["include_eth"] else None
            self._debug = configuration["include_eth"]["debug"] \
                if "debug" in configuration["include_eth"] else False

            # Now, create the WIZNET instance in the carrier board class
            self.eth = WIZNET5K(spi_bus=_spi_bus, cs=_cs, \
                                is_dhcp=self._is_dhcp, \
                                mac=self._mac, hostname=self._hostname, \
                                debug=self._debug)

        if "include_microsd" in configuration and configuration["include_microsd"]:
            # The microSD uses a SPI interface is across fixed pins on the board
            _cs = digitalio.DigitalInOut(self.MICRO_SD_CS)
            _spi_bus = busio.SPI(self.SCK, MOSI=self.MOSI, MISO=self.MISO)

            # Now, create the sdcardio.SDCard instance in the carrier board class
            self.microsd = sdcardio.SDCard(bus=_spi_bus, cs=_cs)

        # Create busio instances for I2C0-I2C2
        if "init_i2c0" in configuration and configuration["init_i2c0"]:
            self.I2C0 = busio.I2C(self.SCL0, self.SDA0)
        if "init_i2c1" in configuration and configuration["init_i2c1"]:
            self.I2C1 = busio.I2C(self.SCL1, self.SDA1)
        if "init_i2c2" in configuration and configuration["init_i2c2"]:
            self.I2C2 = busio.I2C(self.SCL2, self.SDA2)

        if "init_neopixel" in configuration and configuration["init_neopixel"]:
            _num_pixels_on_board = "num_pixels" in configuration["init_neopixel"] if \
                configuration["init_neopixel"]["num_pixels"] else 1
            self.neopixel = neopixel.NeoPixel(self.NEOPIXEL_IF,
                                                 _num_pixels_on_board,
                                                 brightness=0.3, auto_write=False)
            self.neopixel.fill(self.BLACK_COLOR)
            self.neopixel.show()

        self.neopixel_status.fill(self.BOOT_READY_COLOR)
        self.neopixel_status.show()

    def set_as_input(self, pin):
        digitalio.DigitalInOut(pin).direction = digitalio.Direction.INPUT
