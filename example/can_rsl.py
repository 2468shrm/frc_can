"""This doesn't handle the case of a single heartbeat
followed by many non-heartbeat messages.

I think I need to fold this into can_handler and have it inclue a
time knowledge for lacking heartbeats."""

from carrier_board.m4_feather_can import CarrierBoard
from canio import Message, Match
from can_handler import CANHandler
from ids.msg_format import FRCCANDevice
from ids.heartbeat import HeartBeatMsg
from adafruit_ticks import ticks_ms, ticks_less, ticks_add

CarrierBoardConfiguration = {
    "include_can":
    {
        "baudrate": 1000000,
        "auto_restart": True
    },
    "include_eth": False,
    "include_microsd": False,
    "init_i2c0": False,
    "init_i2c1": False,
    "init_i2c2": False,
    "init_neopixel":
    {
        "num_pixels": 1
    }
}

class RobotSignalLight:
    # Colors use by an RSL are...
    ORANGE = (0,0,0)
    RED = (255,0,0)
    BLACK = (0,0,0)

    # The three states of RSL reporting.. 
    DISABLED = 0
    ENABLED = 1
    ERROR = 2

    # During blinking, since it is an RGB LED, we can't just invert
    # the LED, so we need to know whether on or off
    OFF = False
    ON = True

    # The mapping of the RSL in terms of RGB colors to state
    COLOR_STATE = { OFF: BLACK, ON: ORANGE }

    # The number of ms per blink transition (one blink period is two
    # transitions, on and off)
    BLINK_PERIOD_HALF = 125

    # The number of ms that can expire before the device is considered
    # disable
    TIMEOUT_PERIOD = 100   # 0.1s

    def __init__(self, carrier_board):
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

        # Blink information (LEDs on or off, and time for )
        self.blink = self.OFF
        self.cb.neopixel.fill(self.COLOR_STATE[self.blink])
        self.cb.neopixel.show()

        # record the time to re-evaluate
        _now = ticks_ms()
        self.blink_time = ticks_add(_now, self.BLINK_PERIOD_HALF)
        self.timeout_time = ticks_add(_now, self.TIMEOUT_PERIOD) 

    def not_a_heartbeat_msg(self):
        """not_a_heartbeat_msg function is called for any message received by
        CANHandler that isn't a heartbeat. This option of CANHandler is used only
        to look for expired periods without seeing a heart beat message."""
        if ticks_less(self.timeout_time, ticks_ms()):
            self.cb.neopixel.fill(self.RED)
            self.blink = self.ON
            self.state = self.ERROR
            self.cb.neopixel.show()

    def heartbeat_msg(self, message):
        """The heartbeat_msg() function should be called ONLY if a heartbeat message
        was received by CANHandler (we specifically register a message handler
        for this message ID)# """
        self.hb.data = message.data
        if self.hb.system_watchdog:
            # Enabled if system_watchdog bit is set..
            self.state = self.ENABLED
            _now = ticks_ms()
            # Blink the LED, if time..
            if ticks_less(self.blink_time, _now):
                # off to on..
                if self.blink == self.OFF:
                    self.cb.neopixel.fill(self.ORANGE)
                    self.blink = self.ON
                # on to off..
                else:
                    cb.neopixel.fill(self.BLACK)
                    self.blink = self.OFF
                self.cb.neopixel.show()
                self.blink_time = ticks_add(_now, self.BLINK_PERIOD_HALF)
        else:
            # Disabled otherwise
            self.state = self.DISABLED
            cb.neopixel.fill(self.ORANGE)
            self.blink = self.ON
            cb.neopixel.show()
            self.blink_time = ticks_add(ticks_ms(), self.BLINK_PERIOD_HALF)
        # reset the timeout time since we've seen a heart beat..
        self.timeout_time = ticks_add(_now, self.TIMEOUT_PERIOD) 

    def timeout(self, message):
        # The timeout() function should be called ONLY if no message is received
        # during the listen period, which means the heartbeat is not being sent
        cb.neopixel.fill(self.RED)
        self.blink = self.ON
        self.state = self.ERROR
        cb.neopixel.show()
        _now = ticks_ms()
        self.blink_time = ticks_add(_now, self.BLINK_PERIOD_HALF)
        self.timeout_time = ticks_add(_now, self.TIMEOUT_PERIOD) 


# Initialize the carrier board
cb = CarrierBoard(CarrierBoardConfiguration)

# Create the RSL.. 
rsl = RobotSignalLight(carrier_board=cb)

# Setup to receive and parse a hearbeat message
hb = HeartBeatMsg()

# Create a handler instance, marking it to handle all outstanding (queued )
handler = CANHandler(carrier_board=cb, drain_queue=True, timeout=0.1)
# One for decoded heart beats, one for non-decoded heart beats, and
# one for timeouts.
handler.register_handler(hb.id, rsl.heartbeat_msg)
handler.register_timeout_handler(rsl.timeout)
handler.register_register_unmatched_handler(rsl.not_a_heartbeat_msg)

while True:
    handler.step()
