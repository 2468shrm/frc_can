
class FRCCANDevice:
    def __init__(self, device_type=0, manufacturer=0, api=0, device_number=0):
        self.device_type = device_type
        self.manufacturer = manufacturer
        self.api = api
        self.device_number = device_number

    """These are constants for the MessageID bit field"""
    DEVICE_TYPE_LSB = 24
    DEVICE_TYPE_MASK = 0x1f
    MANUFACTURER_LSB = 16
    MANUFACTURER_MASK = 0xff
    API_LSB = 6
    API_MASK = 0x3ff
    DEVICE_NUMBER_LSB = 0
    DEVICE_NUMBER_MASK = 0x3f

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

    """Manufacturer field encodings"""
    MANUFACTURER_BROADCAST = 0
    MANUFACTURER_NI = 1
    MANUFACTURER_LUMINARY_MICRO = 2
    MANUFACTURER_DEKA = 3
    MANUFACTURER_CTR_ELECTRONICS = 4
    MANUFACTURER_REV_ROBOTICS = 5
    MANUFACTURER_GRAPPLE = 6
    MANUFACTURER_MINDSENSORS = 7
    MANUFACTURER_TEAM_USE = 8
    MANUFACTURER_KAUAI_LABS = 9
    MANUFACTURER_COPPERFORGE = 10
    MANUFACTURER_PLAYING_WITH_FUSION = 11
    MANUFACTURER_STUDICA = 12


    def __str__(self) -> str:
        _s = f"device_type: {self.device_type}"
        _s += f"manufacturer: {self.manufacturer}"
        _s += f"api: {self.api}"
        _s += f"device_number: {self.device_number}"
        return _s

        
    def __post_init__(self):
        self.message_id = (self.device_type & self.DEVICE_NUMBER_MASK) << self.DEVICE_TYPE_LSB | \
                          (self.manufacturer & self.MANUFACTURER_MASK) << self.MANUFACTURER_LSB | \
                          (self.api & self.API_MASK) << self.API_LSB | \
                          (self.device_number & self.DEVICE_NUMBER_MASK) << self.DEVICE_NUMBER_LSB


    def update(self, msg_id):
        """Updates the instance value with full MessageID value."""
        self.device_type = (msg_id >> self.DEVICE_TYPE_LSB) & self.DEVICE_NUMBER_MASK
        self.manufacturer = (msg_id >> self.MANUFACTURER_LSB) & self.MANUFACTURER_MASK
        self.api = (msg_id >> self.API_LSB) & self.API_MASK
        self.device_number = (msg_id >> self.DEVICE_NUMBER_LSB) & self.DEVICE_NUMBER_MASK
        self.message_id = msg_id


    def update_device_type(self, device_type):
        """Updates the device type of the instance value."""
        self.device_type = (device_type >> self.DEVICE_TYPE_LSB) & self.DEVICE_NUMBER_MASK
        self.__post_init__()


    def update_manufacturer(self, manufacturer):
        """Updates the manufacturer of the instance value."""
        self.manufacturer = (manufacturer >> self.MANUFACTURER_LSB) & self.MANUFACTURER_MASK
        self.__post_init__()


    def update_api(self, api):
        """Updates the api of the instance value."""
        self.api = (api >> self.API_LSB) & self.API_MASK
        self.__post_init__()


    def update_device_number(self, device_number):
        """Updates the device number of the instance value."""
        self.device_number = (device_number >> self.DEVICE_NUMBER_LSB) & self.DEVICE_NUMBER_MASK
        self.__post_init__()


    def __str__(self) -> str:
        _s  = f"device_type: {self.device_type:x}"
        _s += f" manufacturer: {self.manufacturer:x}"
        _s += f" api: {self.api:x}"
        _s += f" device_number: {self.device_number:x}"
        return _s


"""This is a test wrapper to make sure the above stuff is correct.."""
if __name__ == '__main__':
    test1 = FRCCANDevice()
    expected_value = 0
    if test1.message_id != expected_value:
        raise RuntimeError(f"test1 expected to have value 0x{expected_value:08x}, not 0x{test1.message_id:08x}")
    print(f"test1.message_id value should be 0x{expected_value:08x}, is 0x{test1.message_id:08x}")

    test2 = FRCCANDevice(device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
                        manufacturer=FRCCANDevice.MANUFACTURER_TEAM_USE,
                        api=1,
                        device_number=1)
    expected_value = 0x0a080041
    if test2.message_id != expected_value:
        raise RuntimeError(f"test2 expected to have value 0x{expected_value:08x}, not 0x{test1.message_id:08x}")
    print(f"test2.message_id value should be 0x{expected_value:08x}, is 0x{test2.message_id:08x}")

"""

0x01011840                        0b0_0001_0000_0001_0001_1000_0100_0000
   | |  ||                               |         |            |      |
   | |  |0x00 Device Number (0)          |         |            |      device_number  0b00_0000
   | |  0x61 API (97)                    |         |            api  0b00_0110_0001
   | 0x01 - Manufacturer (1)             |         manufacturer  0b0000_0001
   0x01 - Device Type (1)                device_type  0b0_0001

"""
