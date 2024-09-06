"""This doesn't handle the case of a single heartbeat
followed by many non-heartbeat messages.

I think I need to fold this into can_handler and have it inclue a
time knowledge for lacking heartbeats."""

from carrier_board.m4_feather_can import CarrierBoard
from canio import Match
from can_handler import CANHandler
from ids.heartbeat import HeartBeatMsg
from adafruit_ticks import ticks_ms, ticks_less, ticks_add
import time


class RobotSignalLight:
    # Colors use by an RSL are...
    ORANGE = (255, 69, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)

    # The three states of RSL reporting..
    STATE_DISABLED = 0
    STATE_ENABLED = 1
    STATE_ERROR = 2

    # During blinking, since it is an RGB LED, we can't just invert
    # the LED, so we need to know whether on or off
    OFF = False
    ON = True

    # The mapping of the RSL in terms of RGB colors to state
    COLOR_STATE = {
        STATE_DISABLED: ORANGE,
        STATE_ENABLED: ORANGE,
        STATE_ERROR: RED
    }
    BLINK_STATE = {
        STATE_DISABLED: False,
        STATE_ENABLED: True,
        STATE_ERROR: False
    }

    # The number of ms per blink transition (one blink period is two
    # transitions, on and off)
    BLINK_PERIOD_HALF = 125

    # The number of ms that can expire before the device is considered
    # disable
    TIMEOUT_PERIOD = 100   # 0.1s

    def __init__(self, carrier_board: CarrierBoard) -> None:
        """Simulates a Robot Signal Light (RSL) function by listening to the
        CAN heart beat message. In the heart beat, if the system_watchdog but
        is set, the robot is enabled and the RSL should flash about 4-5 Hz.
        If the system_watchdog is clear, the robot disabled and the RSL should
        display a solid light. When disabled, motor controllers are not
        allowed to energize motors.  We try to catch and display a red light
        if we do not detect a heart beat message in 2 "PWM" periods."""

        # The CarrierBoard object needed to run the Neopixel LEDS
        self.cb = carrier_board
        # A HB message object for parsing
        self.hb = HeartBeatMsg()

        # Initial state..
        self.state = self.STATE_ERROR

        # Blink information (LEDs on or off, and time for )
        self.blink = self.OFF

        # Show the initial colors
        self.cb.neopixel.fill(self.COLOR_STATE[self.state])
        self.cb.neopixel.show()

        # Setup the time in the future to re-evaluate
        _now = ticks_ms()
        self.blink_time = ticks_add(_now, self.BLINK_PERIOD_HALF)
        self.timeout_time = ticks_add(_now, self.TIMEOUT_PERIOD)

    def heartbeat_msg(self, message: HeartBeatMsg) -> None:
        """The heartbeat_msg() function should be called ONLY if a heartbeat
        message was received by CANHandler (we specifically register a
        message handler for this message ID)# """
        _now = ticks_ms()
        self.hb.data = message.data
        if self.hb.system_watchdog:
            # Enabled if system_watchdog bit is set..
            self.state = self.STATE_ENABLED
        else:
            self.state = self.STATE_DISABLED

        # Advance the timeout counter if a heartbeat message was received
        self.timeout_time = ticks_add(_now, self.TIMEOUT_PERIOD)

    def step(self) -> None:
        # Get the current time
        _now = ticks_ms()

        # Check to see if the timeout period has passed.
        # If so, change the state to error and show it
        if ticks_less(self.timeout_time, _now):
            self.state = self.STATE_ERROR
            cb.neopixel.fill(self.COLOR_STATE[self.state])
            cb.neopixel.show()

            self.timeout_time = ticks_add(_now, self.TIMEOUT_PERIOD)
            if ticks_less(self.blink_time, _now):
                self.blink_time = ticks_add(_now, self.BLINK_PERIOD_HALF)

        # If not timed out, it is time to blink the current state?
        elif ticks_less(self.blink_time, _now):
            if self.BLINK_STATE[self.state]:
                # off to on..
                if self.blink == self.OFF:
                    self.cb.neopixel.fill(self.COLOR_STATE[self.state])
                    self.blink = self.ON
                # on to off..
                else:
                    cb.neopixel.fill(self.BLACK)
                    self.blink = self.OFF
            else:
                cb.neopixel.fill(self.COLOR_STATE[self.state])
            self.cb.neopixel.show()

            # Advance the blink time
            self.blink_time = ticks_add(_now, self.BLINK_PERIOD_HALF)


# How much do we initialize the carrier board?  Just the CAN interface and
# Neopixel interface
CarrierBoardConfiguration = {
    "init_can":
    {
        # FRC defaults, baud is 1 Mbps, auto restart
        "baudrate": 1000000,
        "auto_restart": True,
        # Setup a listener to only listen to the heartbeat messages
        "listener_match_list":
            [Match(HeartBeatMsg.HEARTBEAT_ID, extended=True)],
        # A very long timeout
        "timeout": 0.05,
    },
    "init_neopixel":
    {
        "num_pixels": 15
    }
}

# Initialize the carrier board
cb = CarrierBoard(CarrierBoardConfiguration)
cb.status.on((0, 255, 0))

# Create the RSL..
rsl = RobotSignalLight(carrier_board=cb)

# Create a handler instance, marking it to handle all outstanding (queued )
handler = CANHandler(carrier_board=cb, drain_queue=False)

# One for decoded heart beats, one for non-decoded heart beats, and
# one for timeouts.
handler.register_msg_handler(HeartBeatMsg.HEARTBEAT_ID, rsl.heartbeat_msg)

while True:
    handler.step()
    rsl.step()

cb.status.on((255, 0, 0))
time.sleep(1)
