
class FRCCANDevice:
    """These are constants for the MessageID bit field"""
    DEVICE_TYPE_LSB = 24
    DEVICE_TYPE_MASK = 0x1f
    DEVICE_TYPE_MASK_ALL = (DEVICE_TYPE_MASK << DEVICE_TYPE_LSB)

    MANUF_LSB = 16
    MANUF_MASK = 0xff
    MANUF_MASK_ALL = (MANUF_MASK << MANUF_LSB)

    API_LSB = 6
    API_MASK = 0x3ff
    API_MASK_ALL = (API_MASK << API_LSB)
    DEVICE_NUMBER_LSB = 0
    DEVICE_NUMBER_MASK = 0x3f
    DEVICE_NUMBER_MASK_ALL = (DEVICE_NUMBER_MASK << DEVICE_NUMBER_LSB)

    MESSAGE_ID_MASK = DEVICE_TYPE_MASK_ALL | MANUF_MASK_ALL | \
        API_MASK_ALL | DEVICE_NUMBER_MASK_ALL

    DEVICE_TYPE_MASK_EXTRACT = DEVICE_TYPE_MASK_ALL ^ MESSAGE_ID_MASK
    MANUF_MASK_EXTRACT = MANUF_MASK_ALL ^ MESSAGE_ID_MASK
    API_MASK_EXTRACT = API_MASK_ALL ^ MESSAGE_ID_MASK
    DEVICE_NUMBER_MASK_EXTRACT = DEVICE_NUMBER_MASK_ALL ^ MESSAGE_ID_MASK

    """Device Type field encodings"""
    DEVICE_TYPE_BROADCAST = 0
    DEVICE_TYPE_ROBOT_CONTROLLER = 1
    DEVICE_TYPE_MOTOR_CONTROLLER = 2
    DEVICE_TYPE_RELAY_CONTROLLER = 3
    DEVICE_TYPE_GYPO_SENSOR = 4
    DEVICE_TYPE_ACCELEROMETER = 5
    DEVICE_TYPE_ULTRASONIC_SENSOR = 6
    DEVICE_TYPE_GEARTOOTH_SENSOR = 7
    DEVICE_TYPE_POWER_DISTRIBUTION_MODULE = 8
    DEVICE_TYPE_PNEUMATICS_CONTROLLER = 9
    DEVICE_TYPE_MISCELLANEOUS = 10
    DEVICE_TYPE_IO_BREAKOUT = 11
    DEVICE_TYPE_FIRMWARE_UPDATE = 31
    DEVICE_TYPE_DECODE = {0: "Broadcast", 1: "Robot Controller",
                          2: "Motor Controller", 3: "Relay Controller",
                          4: "Gyro", 5: "Accelerometer",
                          6: "Ultrasonic", 7: "Geartooth",
                          8: "Power Dist", 9: "Pneumatics Controller",
                          10: "Misc", 11: "IO Breakout",
                          31: "Firmware Update"}

    """Manufacturer field encodings"""
    MANUF_BROADCAST = 0
    MANUF_NI = 1
    MANUF_LUMINARY_MICRO = 2
    MANUF_DEKA = 3
    MANUF_CTR_ELECTRONICS = 4
    MANUF_REV_ROBOTICS = 5
    MANUF_GRAPPLE = 6
    MANUF_MINDSENSORS = 7
    MANUF_TEAM_USE = 8
    MANUF_KAUAI_LABS = 9
    MANUF_COPPERFORGE = 10
    MANUF_PLAYING_WITH_FUSION = 11
    MANUF_STUDICA = 12
    MANUF_THE_THRIFTY_BOT = 13
    MANUF_REDUX = 14
    MANUF_ANDYMARK = 15
    MANUF_VIVID_HOSTING = 16
    MANUF_DECODE = {MANUF_BROADCAST: "Broadcast",
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
                    MANUF_VIVID_HOSTING: "Vivid Hosting"}

    def __init__(self, device_type=None, manufacturer=None, api=None,
                 device_number=None, message_id=None):
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

    def _insert_device_type(self, device_type):
        self._message_id = (self._message_id &
                            self.DEVICE_TYPE_MASK_EXTRACT) | \
            ((device_type & self.DEVICE_TYPE_MASK) << self.DEVICE_TYPE_LSB)

    def _extract_device_type(self):
        _t = (self._message_id >> self.DEVICE_TYPE_LSB) & self.DEVICE_TYPE_MASK
        return _t

    def _insert_manufacturer(self, manufacturer):
        self._message_id = (self._message_id & self.MANUF_MASK_EXTRACT) | \
            ((manufacturer & self.MANUF_MASK) << self.MANUF_LSB)

    def _extract_manufacturer(self):
        _t = (self._message_id >> self.MANUF_LSB) & self.MANUF_MASK
        return _t

    def _insert_api(self, api):
        self._message_id = (self._message_id & self.API_MASK_EXTRACT) | \
            ((api & self.API_MASK) << self.API_LSB)

    def _extract_api(self):
        _t = (self._message_id >> self.API_LSB) & self.API_MASK
        return _t

    def _insert_device_number(self, device_number):
        self._message_id = (self._message_id &
                            self.DEVICE_NUMBER_MASK_EXTRACT) | \
            ((device_number & self.DEVICE_NUMBER_MASK) <<
             self.DEVICE_NUMBER_LSB)

    def _extract_device_number(self):
        _t = (self._message_id >> self.DEVICE_NUMBER_LSB) & \
              self.DEVICE_NUMBER_MASK
        return _t

    @property
    def device_type(self):
        return self._extract_device_type()

    @device_type.setter
    def device_type(self, value):
        self._insert_device_type(value)

    @property
    def manufacturer(self):
        return self._extract_manufacturer()

    @manufacturer.setter
    def manufacturer(self, value):
        self._insert_manufacturer(value)

    @property
    def api(self):
        return self._extract_api()

    @api.setter
    def api(self, value):
        self._insert_api(value)

    @property
    def device_number(self):
        return self._extract_device_number()

    @device_number.setter
    def device_number(self, value):
        self._insert_device_number(value)

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, value):
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


"""This is a test wrapper to make sure the above stuff is correct.."""
if __name__ == '__main__':
    test1 = FRCCANDevice()
    expected_value = 0
    _err_str = f"test1 expected to have value 0x{expected_value:08x}," + \
        f"not 0x{test1.message_id:08x}"
    if test1.message_id != expected_value:
        raise RuntimeError(_err_str)
    _pass_str = f"PASS: test1.message_id value should be " + \
        f"0x{expected_value:08x}, is 0x{test1.message_id:08x}"
    print(_pass_str)

    test2 = FRCCANDevice(device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
                         manufacturer=FRCCANDevice.MANUF_TEAM_USE,
                         api=1,
                         device_number=1)
    expected_value = 0x0a080041
    if test2.message_id != expected_value:
        _err_str = f"test2 expected to have value 0x{expected_value:08x}," + \
            f" not 0x{test1.message_id:08x}"
        raise RuntimeError(_err_str)
    _pass_str = f"PASS: test2.message_id value should be " + \
        f"0x{expected_value:08x}, is 0x{test2.message_id:08x}"
    print(_pass_str)

    # Universal heartbeat message id..
    uhb = FRCCANDevice(message_id=0x01011840)
    _pass_str = f"Universal heartbeat (message_id of {uhb.message_id})" + \
        f"\n decomposition is {uhb}"
    print(_pass_str)
