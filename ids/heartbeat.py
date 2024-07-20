
# Information for this file derived from
# https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/2468shrm/frc_can.git"


class HeartBeatMsg:
    # The ID of the heart beat system message (from the HTML link above)
    HEARTBEAT_ID = 0x01011840

    # Time of day, hour
    # It occupies 5 bits of byte 0 (bits 7:3)
    # [0]: VVVVV---
    # uint64_t timeOfDay_hr : 5;
    TIME_OF_DAY_HR_BYTE = 0
    TIME_OF_DAY_HR_LSB = 3
    TIME_OF_DAY_HR_MASK = 0x1f

    # Time of day, minute
    # It ocupies 3 bits of byte 0 (bits 2:0)
    #  and 3 bits of byte 1 (bits 7:5)
    # [0]: -----HHH
    # [1]: LLL-----
    # uint64_t timeOfDay_min : 6;
    TIME_OF_DAY_MIN_BYTE_H = 0
    TIME_OF_DAY_MIN_LSB_H = 0
    TIME_OF_DAY_MIN_MASK_H = 0x7
    TIME_OF_DAY_MIN_OVRL_H = 3

    TIME_OF_DAY_MIN_BYTE_L = 1
    TIME_OF_DAY_MIN_LSB_L = 5
    TIME_OF_DAY_MIN_MASK_L = 0x7

    # Time of day, sec
    # It occupies 5 bits of byte 1 (bits 4:0)
    #  and one bit of byte 2 (bit 7)
    # [1]: ---HHHHH
    # [2]: L------
    # uint64_t timeOfDay_sec : 6;
    TIME_OF_DAY_SEC_BYTE_H = 1
    TIME_OF_DAY_SEC_LSB_H = 0
    TIME_OF_DAY_SEC_MASK_H = 0x1f
    TIME_OF_DAY_SEC_OVRL_H = 1

    TIME_OF_DAY_SEC_BYTE_L = 2
    TIME_OF_DAY_SEC_LSB_L = 7
    TIME_OF_DAY_SEC_MASK_L = 1

    # Time of day, day
    # It occupies 5 bits of byte 2 (bits 6:2)
    # [2]: -VVVVV--
    # uint64_t timeOfDay_day : 5;
    TIME_OF_DAY_DAY_BYTE = 2
    TIME_OF_DAY_DAY_LSB = 2
    TIME_OF_DAY_DAY_MASK = 0x1f

    # Time of day, month
    # It occupies 2 bits of byte 2
    #  and 2 bits of byte 3
    # [2]: ------HH
    # [3]: LL------
    # uint64_t timeOfDay_month : 4;
    TIME_OF_DAY_MO_BYTE_H = 2
    TIME_OF_DAY_MO_LSB_H = 0
    TIME_OF_DAY_MO_MASK_H = 3
    TIME_OF_DAY_MO_OVRL_H = 2

    TIME_OF_DAY_MO_BYTE_L = 3
    TIME_OF_DAY_MO_LSB_L = 6
    TIME_OF_DAY_MO_MASK_L = 3

    # Time of day, year
    # It occupies 6 bits of byte 3
    # [3]: --VVVVVV
    # uint64_t timeOfDay_yr : 6;
    TIME_OF_DAY_YR_BYTE = 3
    TIME_OF_DAY_YR_LSB = 0
    TIME_OF_DAY_YR_MASK = 0x3f

    # Tournament type
    # It occupies byte..
    # [4]: VVV-----
    # uint64_t tournamentType : 3;
    TOURNAMENT_TYPE_BYTE = 4
    TOURNAMENT_TYPE_LSB = 5
    TOURNAMENT_TYPE_MASK = 7

    # System watchdog
    # It occupies byte..
    # [4]: ---V----
    # uint64_t systemWatchdog : 1;
    SYSTEM_WATCHDOG_BYTE = 4
    SYSTEM_WATCHDOG_LSB = 4
    SYSTEM_WATCHDOG_MASK = 1

    # Test mode
    # It occupies byte..
    # [4]: ----V---
    # uint64_t testMode : 1;
    TEST_MODE_BYTE = 4
    TEST_MODE_LSB = 3
    TEST_MODE_MASK = 1

    # Autonomous
    # It occupies byte..
    # [4]: -----V--
    # uint64_t autonomous : 1;
    AUTONOMOUS_BYTE = 4
    AUTONOMOUS_LSB = 2
    AUTONOMOUS_MASK = 1

    # Enabled
    # It occupies byte..
    # [4]: ------V-
    # uint64_t enabled : 1;
    ENABLE_BYTE = 4
    ENABLED_LSB = 1
    ENABLED_MASK = 1

    # Red alliance
    # It occupies byte...
    # [4]: -------V
    # uint64_t redAlliance : 1;
    RED_ALLIANCE_BYTE = 4
    RED_ALLIANCE_LSB = 0
    RED_ALLIANCE_MASK = 1

    # Replay number
    # It occupies 6 bits of byte 5 (bits 5:0)
    # [5]: VVVVVV--
    # uint64_t replayNumber : 6;
    REPLAY_NUMBER_BYTE = 5
    REPLAY_NUMBER_LSB = 2
    REPLAY_NUMBER_MASK = 0x3f

    # Match number
    # It occupies 2 bits of byte 5 (bits 7:6)
    #  and 8 bits of byte 6 (bita 7:0)
    # [5]: ------HH
    # [6]: LLLLLLLL
    # uint64_t matchNumber : 10;
    MATCH_NUMBER_BYTE_H = 5
    MATCH_NUMBER_LSB_H = 0
    MATCH_NUMBER_MASK_H = 0x3
    MATCH_NUMBER_OVRL_H = 8

    MATCH_NUMBER_BYTE_L = 6
    MATCH_NUMBER_LSB_L = 0
    MATCH_NUMBER_MASK_L = 0xff

    # Match time, in seconds
    # It occupies 8 bits of byte 7 (bits 7:0)
    # [7]: VVVVVVVV
    # uint64_t matchTimeSeconds : 8;
    MATCH_TIME_BYTE = 7
    MATCH_TIME_LSB = 0
    MATCH_TIME_MASK = 0xff

    def __init__(self, data: bytearray = None) -> None:
        """Heart beat message object.
        Args
           data (bytearray): Message body of CAN heart beat message."""
        self._data = data if data else bytearray(8)

    def _extract_single(self, byte: int, lsb: int, mask: int) -> int:
        _t = (self._data[byte] >> lsb) & mask
        return _t

    def _extract_pair(self, byteh: int, lsbh: int, maskh: int,
                      bytel: int, lsbl: int, maskl: int,
                      upper_lsb: int) -> int:
        _t_upper = self._extract_single(byteh, lsbh, maskh)
        _t_lower = self._extract_single(bytel, lsbl, maskl)
        _t = (_t_upper << upper_lsb) + _t_lower
        return _t

    def _insert_single(self, value: int, byte: int, lsb: int,
                       mask: int) -> int:
        # clear data first..
        _t = self._data[byte] & ~(mask << lsb)
        # mask off un-used values outside the mask
        _v = value & mask
        # or the values together to isnert
        _t = _t | (_v << lsb)
        # save it back to the byte
        self._data[byte] = _t

    @property
    def id(self) -> int:
        """The MessageID of a heartbeat message object. Useful for establishing
        a filter."""
        return self.HEARTBEAT_ID

    @property
    def data(self) -> bytearray:
        """The payloa data for the heartbeat message object."""
        return self._data

    @data.setter
    def data(self, byte_value: bytearray) -> None:
        """Set the payload data directly."""
        self._data = byte_value

    @property
    def match_time(self) -> int:
        """Returns the match time, in seconds, as embedded in the
        heartbeat message object."""
        return self._data[self.MATCH_TIME_BYTE]

    @match_time.setter
    def match_time(self, value: int) -> None:
        """Sets the match time, in seconds, into the message object
        payload."""
        self._data[self.MATCH_TIME_BYTE] = value

    @property
    def match_number(self) -> int:
        return self._extract_pair(
            self.MATCH_NUMBER_BYTE_H,
            self.MATCH_NUMBER_LSB_H,
            self.MATCH_NUMBER_MASK_H,
            self.MATCH_NUMBER_BYTE_L,
            self.MATCH_NUMBER_LSB_L,
            self.MATCH_NUMBER_MASK_L,
            self.MATCH_NUMBER_OVRL_H
        )
        # 6, 0, 0xff, 5, 0, 0x3, 2)

    @match_number.setter
    def match_number(self, value: int) -> None:
        self._insert_single(
            (value >> self.MATCH_NUMBER_OVRL_H),
            self.MATCH_NUMBER_BYTE_H,
            self.MATCH_NUMBER_LSB_H,
            self.MATCH_NUMBER_MASK_H
        )
        self._insert_single(
            value,
            self.MATCH_NUMBER_BYTE_L,
            self.MATCH_NUMBER_LSB_L,
            self.MATCH_NUMBER_MASK_L
        )

    @property
    def replay_number(self) -> int:
        return self._extract_single(5, 2, 0x3f)

    @replay_number.setter
    def replay_number(self, value: int) -> None:
        self._insert_single(value, 5, 2, 0x3f)

    @property
    def red_alliance(self) -> int:
        return self._extract_single(
            self.RED_ALLIANCE_BYTE,
            self.RED_ALLIANCE_LSB,
            self.RED_ALLIANCE_MASK
        )

    @red_alliance.setter
    def red_alliance(self, value: int) -> None:
        self._insert_single(
            value,
            self.RED_ALLIANCE_BYTE,
            self.RED_ALLIANCE_LSB,
            self.RED_ALLIANCE_MASK
        )

    @property
    def enabled(self) -> int:
        return self._extract_single(
            self.ENABLE_BYTE,
            self.ENABLED_LSB,
            self.ENABLED_MASK
        )

    @enabled.setter
    def enabled(self, value: int) -> None:
        self._insert_single(
            value,
            self.ENABLE_BYTE,
            self.ENABLED_LSB,
            self.ENABLED_MASK
        )

    @property
    def autonomous(self) -> int:
        return self._extract_single(
            self.AUTONOMOUS_BYTE,
            self.AUTONOMOUS_LSB,
            self.AUTONOMOUS_MASK
        )

    @autonomous.setter
    def autonomous(self, value: int) -> None:
        self._insert_single(
            value,
            self.AUTONOMOUS_BYTE,
            self.AUTONOMOUS_LSB,
            self.AUTONOMOUS_MASK
        )

    @property
    def test_mode(self) -> int:
        return self._extract_single(
            self.TEST_MODE_BYTE,
            self.TEST_MODE_LSB,
            self.TEST_MODE_MASK
        )

    @test_mode.setter
    def test_mode(self, value: int) -> None:
        self._insert_single(
            value,
            self.TEST_MODE_BYTE,
            self.TEST_MODE_LSB,
            self.TEST_MODE_MASK
        )

    @property
    def system_watchdog(self) -> int:
        return self._extract_single(
            self.SYSTEM_WATCHDOG_BYTE,
            self.SYSTEM_WATCHDOG_LSB,
            self.SYSTEM_WATCHDOG_MASK
        )

    @system_watchdog.setter
    def system_watchdog(self, value: int) -> None:
        self._insert_single(
            value,
            self.SYSTEM_WATCHDOG_BYTE,
            self.SYSTEM_WATCHDOG_LSB,
            self.SYSTEM_WATCHDOG_MASK
        )

    @property
    def tournament_type(self) -> int:
        return self._extract_single(
            self.TOURNAMENT_TYPE_BYTE,
            self.TOURNAMENT_TYPE_LSB,
            self.TOURNAMENT_TYPE_MASK
        )

    @tournament_type.setter
    def tournament_type(self, value: int) -> None:
        self._insert_single(
            value,
            self.TOURNAMENT_TYPE_BYTE,
            self.TOURNAMENT_TYPE_LSB,
            self.TOURNAMENT_TYPE_MASK
        )

    @property
    def time_of_day_year(self) -> int:
        return self._extract_single(
            self.TIME_OF_DAY_YR_BYTE,
            self.TIME_OF_DAY_YR_LSB,
            self.TIME_OF_DAY_YR_MASK
        )

    @time_of_day_year.setter
    def time_of_day_year(self, value: int) -> None:
        self._insert_single(
            value,
            self.TIME_OF_DAY_YR_BYTE,
            self.TIME_OF_DAY_YR_LSB,
            self.TIME_OF_DAY_YR_MASK
        )

    @property
    def time_of_day_month(self) -> int:
        return self._extract_pair(
            self.TIME_OF_DAY_MO_BYTE_H,
            self.TIME_OF_DAY_MO_LSB_H,
            self.TIME_OF_DAY_MO_MASK_H,
            self.TIME_OF_DAY_MO_BYTE_L,
            self.TIME_OF_DAY_MO_LSB_L,
            self.TIME_OF_DAY_MO_MASK_L,
            self.TIME_OF_DAY_MO_OVRL_H
        )

    @time_of_day_month.setter
    def time_of_day_month(self, value: int) -> None:
        self._insert_single(
            (value >> self.TIME_OF_DAY_MO_OVRL_H),
            self.TIME_OF_DAY_MO_BYTE_H,
            self.TIME_OF_DAY_MO_LSB_H,
            self.TIME_OF_DAY_MO_MASK_H
        )
        self._insert_single(
            value,
            self.TIME_OF_DAY_MO_BYTE_L,
            self.TIME_OF_DAY_MO_LSB_L,
            self.TIME_OF_DAY_MO_MASK_L
        )

    @property
    def time_of_day_day(self) -> int:
        return self._extract_single(
            self.TIME_OF_DAY_DAY_BYTE,
            self.TIME_OF_DAY_DAY_LSB,
            self.TIME_OF_DAY_DAY_MASK)

    @time_of_day_day.setter
    def time_of_day_day(self, value: int) -> None:
        self._insert_single(
            value,
            self.TIME_OF_DAY_DAY_BYTE,
            self.TIME_OF_DAY_DAY_LSB,
            self.TIME_OF_DAY_DAY_MASK
        )

    @property
    def time_of_day_sec(self) -> int:
        return self._extract_pair(
            self.TIME_OF_DAY_SEC_BYTE_H,
            self.TIME_OF_DAY_SEC_LSB_H,
            self.TIME_OF_DAY_SEC_MASK_H,
            self.TIME_OF_DAY_SEC_BYTE_L,
            self.TIME_OF_DAY_SEC_LSB_L,
            self.TIME_OF_DAY_SEC_MASK_L,
            self.TIME_OF_DAY_SEC_OVRL_H
        )

    @time_of_day_sec.setter
    def time_of_day_sec(self, value: int) -> None:
        self._insert_single(
            (value >> self.TIME_OF_DAY_SEC_OVRL_H),
            self.TIME_OF_DAY_SEC_BYTE_H,
            self.TIME_OF_DAY_SEC_LSB_H,
            self.TIME_OF_DAY_SEC_MASK_H
        )
        self._insert_single(
            value,
            self.TIME_OF_DAY_SEC_BYTE_L,
            self.TIME_OF_DAY_SEC_LSB_L,
            self.TIME_OF_DAY_SEC_MASK_L
        )

    @property
    def time_of_day_min(self) -> int:
        return self._extract_pair(
            self.TIME_OF_DAY_MIN_BYTE_H,
            self.TIME_OF_DAY_MIN_LSB_H,
            self.TIME_OF_DAY_MIN_MASK_H,
            self.TIME_OF_DAY_MIN_BYTE_L,
            self.TIME_OF_DAY_MIN_LSB_L,
            self.TIME_OF_DAY_MIN_MASK_L,
            self.TIME_OF_DAY_MIN_OVRL_H
        )

    @time_of_day_min.setter
    def time_of_day_min(self, value: int) -> None:
        # The upper part of the TODM field
        self._insert_single(
            value >> self.TIME_OF_DAY_MIN_OVRL_H,
            self.TIME_OF_DAY_MIN_BYTE_H,
            self.TIME_OF_DAY_MIN_LSB_H,
            self.TIME_OF_DAY_MIN_MASK_H
        )
        # The lower part of the TODM field
        self._insert_single(
            value,
            self.TIME_OF_DAY_MIN_BYTE_L,
            self.TIME_OF_DAY_MIN_LSB_L,
            self.TIME_OF_DAY_MIN_MASK_L
        )

    @property
    def time_of_day_hr(self) -> int:
        """Gets the hour field of the time of day of the heartbeat
        message object."""
        return self._extract_single(
            self.TIME_OF_DAY_HR_BYTE,
            self.TIME_OF_DAY_HR_LSB,
            self.TIME_OF_DAY_HR_MASK
        )

    @time_of_day_hr.setter
    def time_of_day_hr(self, value: int) -> None:
        """Sets the hour field of the time of day of the heartbeat
        message object."""
        self._insert_single(
            value,
            self.TIME_OF_DAY_HR_BYTE,
            self.TIME_OF_DAY_HR_LSB,
            self.TIME_OF_DAY_HR_MASK
        )

    def __str__(self) -> str:
        """String representation of the object's data value."""
        _s = (
            "Heartbeat data:\n"
            f" time/date: {self.time_of_day_hr}:"
            f"{self.time_of_day_min}:"
            f"{self.time_of_day_sec} "
            f"{self.time_of_day_day}/"
            f"{self.time_of_day_month}/"
            f"{self.time_of_day_year}\n"
            f" tournament_type: {self.tournament_type}\n"
            f" system_watchdog: {self.system_watchdog}\n"
            f" test_mode: {self.test_mode}\n"
            f" autonomous: {self.autonomous}\n"
            f" enabled: {self.enabled}\n"
            f" red_alliance {self.red_alliance}\n"
            f" replay_number: {self.replay_number}\n"
            f" match number: {self.match_number}\n"
            f" match time: {self.match_time} s"
        )
        _s2 = "\n"
        for b in range(8):
            _s2 += f"{self.data[b]:02x}"
            if b != 7:
                _s2 += ":"
        return _s + " " + _s2
