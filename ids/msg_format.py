
from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/2468shrm/frc_can.git"


class FRCCANDevice:
    """These are constants for the MessageID bit field"""
    DEVICE_TYPE_LSB = const(24)
    DEVICE_TYPE_MASK = const(0x1f)
    DEVICE_TYPE_MASK_ALL = const((DEVICE_TYPE_MASK) << (DEVICE_TYPE_LSB))

    MANUF_LSB = const(16)
    MANUF_MASK = const(0xff)
    MANUF_MASK_ALL = const((MANUF_MASK) << (MANUF_LSB))

    API_LSB = const(6)
    API_MASK = const(0x3ff)
    API_MASK_ALL = const((API_MASK) << (API_LSB))
    DEVICE_NUMBER_LSB = const(0)
    DEVICE_NUMBER_MASK = const(0x3f)
    DEVICE_NUMBER_MASK_ALL = const((DEVICE_NUMBER_MASK) << (DEVICE_NUMBER_LSB))

    MESSAGE_ID_MASK = const(
        (DEVICE_TYPE_MASK_ALL) |
        (MANUF_MASK_ALL) |
        (API_MASK_ALL) |
        (DEVICE_NUMBER_MASK_ALL)
    )

    DEVICE_TYPE_MASK_EXTRACT = const(
        (DEVICE_TYPE_MASK_ALL) ^ (MESSAGE_ID_MASK)
    )
    MANUF_MASK_EXTRACT = const(
        (MANUF_MASK_ALL) ^ (MESSAGE_ID_MASK)
    )
    API_MASK_EXTRACT = const(
        (API_MASK_ALL) ^ (MESSAGE_ID_MASK)
    )
    DEVICE_NUMBER_MASK_EXTRACT = const(
        (DEVICE_NUMBER_MASK_ALL) ^ (MESSAGE_ID_MASK)
    )

    """Device Type field encodings"""
    DEVICE_TYPE_BROADCAST = const(0)
    DEVICE_TYPE_ROBOT_CONTROLLER = const(1)
    DEVICE_TYPE_MOTOR_CONTROLLER = const(2)
    DEVICE_TYPE_RELAY_CONTROLLER = const(3)
    DEVICE_TYPE_GYPO_SENSOR = const(4)
    DEVICE_TYPE_ACCELEROMETER = const(5)
    DEVICE_TYPE_ULTRASONIC_SENSOR = const(6)
    DEVICE_TYPE_GEARTOOTH_SENSOR = const(7)
    DEVICE_TYPE_POWER_DISTRIBUTION_MODULE = const(8)
    DEVICE_TYPE_PNEUMATICS_CONTROLLER = const(9)
    DEVICE_TYPE_MISCELLANEOUS = const(10)
    DEVICE_TYPE_IO_BREAKOUT = const(11)
    DEVICE_TYPE_FIRMWARE_UPDATE = const(31)
    DEVICE_TYPE_DECODE = {
        0: "Broadcast", 1: "Robot Controller",
        2: "Motor Controller", 3: "Relay Controller",
        4: "Gyro", 5: "Accelerometer",
        6: "Ultrasonic", 7: "Geartooth",
        8: "Power Dist", 9: "Pneumatics Controller",
        10: "Misc", 11: "IO Breakout",
        31: "Firmware Update"
    }

    """Manufacturer field encodings"""
    MANUF_BROADCAST = const(0)
    MANUF_NI = const(1)
    MANUF_LUMINARY_MICRO = const(2)
    MANUF_DEKA = const(3)
    MANUF_CTR_ELECTRONICS = const(4)
    MANUF_REV_ROBOTICS = const(5)
    MANUF_GRAPPLE = const(6)
    MANUF_MINDSENSORS = const(7)
    MANUF_TEAM_USE = const(8)
    MANUF_KAUAI_LABS = const(9)
    MANUF_COPPERFORGE = const(10)
    MANUF_PLAYING_WITH_FUSION = const(11)
    MANUF_STUDICA = const(12)
    MANUF_THE_THRIFTY_BOT = const(13)
    MANUF_REDUX = const(14)
    MANUF_ANDYMARK = const(15)
    MANUF_VIVID_HOSTING = const(16)
    MANUF_DECODE = {
        MANUF_BROADCAST: "Broadcast",
        MANUF_NI: "NI",
        MANUF_LUMINARY_MICRO: "Luminary Micro",
        MANUF_DEKA: "DEKA",
        MANUF_CTR_ELECTRONICS: "CTRE",
        MANUF_REV_ROBOTICS: "REV",
        MANUF_GRAPPLE: "Grapple",
        MANUF_MINDSENSORS: "Mindsensors",
        MANUF_TEAM_USE: "Team Use",
        MANUF_KAUAI_LABS: "Kauai Labs",
        MANUF_COPPERFORGE: "Copperforge",
        MANUF_PLAYING_WITH_FUSION: "Playing With Fusion",
        MANUF_STUDICA: "Studica",
        MANUF_THE_THRIFTY_BOT: "The Thrifty Bot",
        MANUF_REDUX: "Redux",
        MANUF_ANDYMARK: "AndyMark",
        MANUF_VIVID_HOSTING: "Vivid Hosting"
    }

    def __init__(self, device_type=None, manufacturer=None, api=None,
                 device_number=None, message_id=None) -> None:
        """FRCCANDevice provides support for generating CAN messages for FRC
        robot applications. This is because FRC uses a specific MessageID
        format.

        Args:
            device_type (int): The device type of the CAN device. Thia
                includes the DEVICE_TYPE_* constants.
            manufacturer (int): The manufacturer code for the CAN device.
                This includes the MANUF_* constants.
            api (int): The API identifier of the operation. There are no
                provided constants for the api since you should be
                generating them, not me.
            device_number (int): Specifics which device being accessed.
                Device number constants are similarly not provided, either.
                I don't have to tell you why, I hope.
            message_id (int): Fully formed MessageID. Useful for development
                and debugging.
        """
        if message_id:
            self._message_id = message_id
        else:
            self._message_id = 0
            if device_type:
                self._insert_device_type(device_type)
            if manufacturer:
                self._insert_manufacturer(manufacturer)
            if api:
                self._insert_api(api)
            if device_number:
                self._insert_device_number(device_number)

    def _insert_device_type(self, device_type: int) -> None:
        self._message_id = (
            self._message_id & self.DEVICE_TYPE_MASK_EXTRACT
            ) | ((device_type & self.DEVICE_TYPE_MASK) << self.DEVICE_TYPE_LSB)

    def _extract_device_type(self) -> int:
        _t = (self._message_id >> self.DEVICE_TYPE_LSB) & self.DEVICE_TYPE_MASK
        return _t

    def _insert_manufacturer(self, manufacturer: int) -> None:
        self._message_id = (self._message_id & self.MANUF_MASK_EXTRACT) | (
            (manufacturer & self.MANUF_MASK) << self.MANUF_LSB
        )

    def _extract_manufacturer(self) -> int:
        _t = (self._message_id >> self.MANUF_LSB) & self.MANUF_MASK
        return _t

    def _insert_api(self, api: int) -> None:
        self._message_id = (self._message_id & self.API_MASK_EXTRACT) | \
            ((api & self.API_MASK) << self.API_LSB)

    def _extract_api(self) -> int:
        _t = (self._message_id >> self.API_LSB) & self.API_MASK
        return _t

    def _insert_device_number(self, device_number: int) -> None:
        self._message_id = (self._message_id &
                            self.DEVICE_NUMBER_MASK_EXTRACT) | \
            ((device_number & self.DEVICE_NUMBER_MASK) <<
             self.DEVICE_NUMBER_LSB)

    def _extract_device_number(self) -> None:
        _t = (self._message_id >> self.DEVICE_NUMBER_LSB) & \
              self.DEVICE_NUMBER_MASK
        return _t

    @property
    def device_type(self) -> int:
        return self._extract_device_type()

    @device_type.setter
    def device_type(self, value: int) -> None:
        self._insert_device_type(value)

    @property
    def manufacturer(self) -> int:
        return self._extract_manufacturer()

    @manufacturer.setter
    def manufacturer(self, value: int) -> None:
        self._insert_manufacturer(value)

    @property
    def api(self) -> int:
        return self._extract_api()

    @api.setter
    def api(self, value):
        self._insert_api(value)

    @property
    def device_number(self) -> int:
        return self._extract_device_number()

    @device_number.setter
    def device_number(self, value: int) -> None:
        self._insert_device_number(value)

    @property
    def message_id(self) -> int:
        return self._message_id

    @message_id.setter
    def message_id(self, value: int) -> None:
        self._message_id = value

    def __str__(self) -> str:
        _device_type = self._extract_device_type()
        _s = f"device_type: {_device_type:x}"
        if _device_type in self.DEVICE_TYPE_DECODE:
            _s += f" ({self.DEVICE_TYPE_DECODE[_device_type]})"

        _manufacturer = self._extract_manufacturer()
        _s += f" manufacturer: {_manufacturer}"
        if _manufacturer in self.MANUF_DECODE:
            _s += f" ({self.MANUF_DECODE[_manufacturer]})"

        _s += f" api: 0x{self._extract_api():x}"
        _s += f" device_number: 0x{self._extract_device_number():x}"
        return _s
