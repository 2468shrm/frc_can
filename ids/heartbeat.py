
# Information for this file derived from
# https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html

from struct import pack_into

class HeartBeatMsg:
    # The ID of the 
    HEARTBEAT_ID = 0x01011840
 
    def __init__(self, data=None):
        self._data = data if data else bytearray(8)

    def _extract_single(self, byte, lsb, mask):
        _t = (self._data[byte] > lsb) & mask
        return _t

    def _extract_pair(self, byte1, lsb1, mask1, byte0, lsb0, mask0, upper_lsb):
        _t_upper = self._extract_single(byte1, lsb1, mask1)
        _t_lower = self._extract_single(byte0, lsb0, mask0)
        _t = (_t_upper << upper_lsb) + _t_lower
        return _t

    def _insert_single(self, value, byte, lsb, mask):
        # clear data first..
        _t = self._data[byte] & ~(mask << lsb)
        _v = value & mask
        _t = _t | (_v << lsb)
        self._data[byte] = _t

    @property
    def id(self):
        return self.HEARTBEAT_ID

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, byte_value):
        self._data = byte_value

    @property
    def match_time(self):
        """match number is byte 8"""
        return self._data[7]

    @match_time.setter
    def match_time(self, value):
        self._data[7] = value

    @property
    def match_number(self):
        return self._extract_pair(6, 0, 0xff, 5, 0, 0x3, 2)

    @match_number.setter
    def match_number(self, value):
        self._insert_single(value >> 2, 6, 0, 0xff)
        self._insert_single(value, 5, 0, 0x3)

    @property
    def replay_number(self):
        return self._extract_single(5, 2, 0x3f)

    @replay_number.setter
    def replay_number(self, value):
        self._insert_single(value, 5, 2, 0x3f)

    @property
    def red_alliance(self):
        return self._extract_single(4, 0, 1)

    @red_alliance.setter
    def red_alliance(self, value):
        self._insert_single(value, 4, 0, 1)

    @property
    def enabled(self):
        return self._extract_single(4, 1, 1)

    @enabled.setter
    def enabled(self, value):
        self._insert_single(value, 4, 1, 1)

    @property
    def autonomous(self):
        return self._extract_single(4, 2, 1)

    @autonomous.setter
    def autonomous(self, value):
        self._insert_single(value, 4, 2, 1)

    @property
    def test_mode(self):
        return self._extract_single(4, 3, 1)

    @test_mode.setter
    def test_mode(self, value):
        self._insert_single(value, 4, 3, 1)

    @property
    def system_watchdog(self):
        return self._extract_single(4, 4, 1)

    @system_watchdog.setter
    def system_watchdog(self, value):
        self._insert_single(value, 4, 4, 1)

    @property
    def tournament_type(self):
        return self._extract_single(4, 5, 7)

    @tournament_type.setter
    def tournament_type(self, value):
        self._insert_single(value, 4, 5, 7)

    @property
    def time_of_day_yr(self):
        return self._extract_single(3, 0, 0x3f)

    @time_of_day_yr.setter
    def time_of_day_yr(self, value):
        self._insert_single(value, 3, 0, 0x3f)

    @property
    def time_of_day_month(self):
        return self._extract_pair(2, 0, 3, 3, 6, 3, 2)

    @time_of_day_month.setter
    def time_of_day_month(self, value):
        self._insert_single(value >> 2, 2, 0, 3)
        self._insert_single(value, 3, 6, 3)

    @property
    def time_of_day_day(self):
        return self._extract_single(2, 2, 0x1f)

    @time_of_day_day.setter
    def time_of_day_day(self, value):
        self._insert_single(value, 2, 2, 0x1f)

    @property
    def time_of_day_sec(self):
        return self._extract_single(1, 0, 0x3f)

    @time_of_day_sec.setter
    def time_of_day_sec(self, value):
        self._insert_single(value >> 1, 1, 0, 0x3f)
        self._insert_single(value, 2, 7, 1)

    @property
    def time_of_day_min(self):
        return self._extract_pair(0, 0, 7, 1, 5, 7, 3)

    @time_of_day_min.setter
    def time_of_day_min(self, value):
        self._insert_single(value >> 3, 0, 0, 0x7)
        self._insert_single(value, 1, 5, 0x7)

    @property
    def time_of_day_hr(self):
        return self._extract_single(0, 3, 0x1f)

    @time_of_day_hr.setter
    def time_of_day_hr(self, value):
        self._insert_single(value, 0, 3, 0x1f)

    def __str__(self):
        _s = "Heartbeat data:\n"
        _s += f" time/date: {self.time_of_day_hr}:"
        _s += f"{self.time_of_day_min}:"
        _s += f"{self.time_of_day_sec} "
        _s += f"{self.time_of_day_day}/"
        _s += f"{self.time_of_day_month}/"
        _s += f"{self.time_of_day_yr}\n"
        _s += f" tournament_type: {self.tournament_type}\n"
        _s += f" system_watchdog: {self.system_watchdog}\n"
        _s += f" test_mode: {self.test_mode}\n"
        _s += f" autonomous: {self.autonomous}\n"
        _s += f" enabled: {self.enabled}\n"
        _s += f" red_alliance {self.red_alliance}\n"
        _s += f" replay_number: {self.replay_number}\n"
        _s += f" match number: {self.match_number}\n"
        _s += f" match time: {self.match_time} s"
        return _s


if __name__ == "__main__":
    buff = bytearray(8)

    alignment = 0x0102030405060708
    extracted_alignment = pack_into(">Q", buff, 0, alignment)
    print(f"alignment: {alignment:x} buff: {buff}")
    print("")

    time_of_day_hr = 0xf800000000000000
    extracted_time_of_day_hr = pack_into(">Q", buff, 0, time_of_day_hr)
    print(f"time_of_day_hr: {time_of_day_hr:x} buff: {buff}")
    print("")

    hb = HeartBeatData()
    print(f"heartbeat (<empty>): {hb.data}")
    hb.match_time = 0xff
    print(f"heartbeat (+match_time): {hb.data}")
    hb.enabled = 1
    print(f"heartbeat (+enabled): {hb.data}")
    hb.system_watchdog = 1
    print(f"heartbeat (+system_watchdog): {hb.data}")
    hb.red_alliance = 1
    print(f"heartbeat (+red_alliance): {hb.data}")
    hb.autonomous = 1
    print(f"heartbeat (+autonomous): {hb.data}")
    hb.test_mode = 1
    print(f"heartbeat (+test_mode): {hb.data}")
    hb.tournament_type = 7
    print(f"heartbeat (+tournament_type): {hb.data}")
    hb.replay_number = 0x3f
    print(f"heartbeat (+replay_number): {hb.data}")
    hb.match_number = 0x3ff
    print(f"heartbeat (+match_number): {hb.data}")

    hb.time_of_day_yr = 0x3f
    print(f"heartbeat (+time_of_day_yr): {hb.data}")
    hb.time_of_day_month = 0xf
    print(f"heartbeat (+time_of_day_month): {hb.data}")
    hb.time_of_day_day = 0x1f
    print(f"heartbeat (+time_of_day_day): {hb.data}")
    hb.time_of_day_sec = 0x3f
    print(f"heartbeat (+time_of_day_sec): {hb.data}")
    hb.time_of_day_min = 0x3f
    print(f"heartbeat (+time_of_day_min): {hb.data}")
    hb.time_of_day_hr = 0x1f
    print(f"heartbeat (+time_of_day_hr): {hb.data}")

    hb_seq = HeartBeatData()
    hb_seq.match_time = 0
    hb_seq.system_watchdog = 1
    hb_seq.match_number = 21
    print(f"hb_seq: {hb_seq.data}")

    hb_seq.match_time = hb_seq.match_time + 1
    print(f"hb_seq: {hb_seq.data}")

    hb_seq.match_time = hb_seq.match_time + 1
    print(f"hb_seq: {hb_seq.data}")

    hb_seq.match_time = hb_seq.match_time + 1
    print(f"hb_seq: {hb_seq.data}")

    hb_seq.match_time += 1
    print(f"hb_seq: {hb_seq.data}")
