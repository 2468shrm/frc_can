
import board
import digitalio
import busio
from canio import Message, Match

"""
Eventually, put this in the CarrierBoard for PicoW
if "raspberry_pi_pico" in board.board_id:
    # either Pico or Pico W
    from adafruit_mcp2515.canio import Message, RemoteTransmissionRequest
    from adafruit_mcp2515 import MCP2515 as CAN
else:
    from canio import Message, RemoteTransmissionRequest
    from canio import CAN
"""

class CANHandler:
    def __init__(self, carrier_board, drain_queue=False, timeout=0.1):
        """
            CANHandler provides a convenient framework for building robotics
            applications using Adafruit and Raspberry Pi boards.  They're even
            more useful if the boards are plugged into the Carrier Boards
            we designed for FRC.

            In particular the Adafruit Feather M4 CAN Express (4759) or the
            Raspberry Pi Pico W combined with an Adafruit Picowbell CAN Bus
            (5728).  It may work with an Adafruit RP2040 CAN Bus Feather
            (5724), but it hasn't been tested.
        """
        # The carrier board passed to the handler for sending messages
        self.cb = carrier_board

        # Process all received messages during timeout slot
        self.drain_queue = drain_queue

        # timeout
        self.timeout = timeout

        # Functions run each iteration step
        self.iteration_function = None

        # an optional timeout function that can be run, but only if
        # set and a message is not received in timeout period
        self.timeout_function = None

        # A table for mapping Messages to a handler function
        self.handler_table = {}

        # A table for mapping RemoteTransmissionRequest to a
        # handler function
        self.rtr_handler_table = {}

    def send(self, msg):
        """Sends a message. Typically used for status transmissions."""
        self.cb.can.send(msg)

    def register_handler(self, message_id, function):
        """Adds a function (handler) to process a message. These are added
        to a dict with message_id as key, function reference as value.
        When a message arrives, if a handler is registered, it is called."""
        if message_id in self.handler_table:
            print("ERROR: Attempting to add MessageID that was"
                  " pre-registered")
            return
        self.handler_table[message_id] = function

    def register_rtr_handler(self, message_id, function):
        """Adds a function (handler) to process a message. These are added
        to a dict with message_id as key, function reference as value.
        When a message arrives, if a handler is registered, it is called."""
        if message_id in self.rtr_handler_table:
            print("ERROR: Attempting to add MessageID that was "
                  "pre-registered")
            return
        self.rtr_handler_table[message_id] = function

    def register_timeout_handler(self, function):
        """Adds a function (handler) to call in the event that a CAN
        message was not receive during the timeout period. The idea is to
        use this to detect a missing heartbeat message."""
        self.timeout_function = function

    """Example handler for RemoteTransmissionRequest handling.
    def example_rtr_handler(message):
        reply_data = struct.pack(format, source_of_data)
        reply_message = Message(id=message.id,
                                      data=reply_data,
                                      extended=message.extended)
        retirm reply_message
    """

    def set_timeout(self, timeout):
        """Be able to change the timeout following the constructor."""
        self.timeout = timeout

    def register_iteration(self, iteration_function):
        """Setup a function to be called when a CAN message does not
        arrive. Examples include sampling and processing I/Os for
        indexing, reading sensors over I2C, SPI, etc."""
        if isinstance(iteration_function, list):
            self.iteration_function = iteration_function
        else:
            # store as a list, even a single entry list
            self.iteration_function = [iteration_function]

    def step(self):
        """Wait for the arrival of a message or a timeout. The message
        can be a Message or a RemoteTransmissionRequest. If one arrives,
        process it. Whether a message/RTR arrives or not, call the
        "iteration" function make progress on processing things needed."""
        message = self.listener.receive()
        if message:
            # A CAN message was received...
            if isinstance(message, Message):
                # it is a Message..
                if message.id in self.handler_table:
                    # And we are setup to process it...
                    return_message = self.handler_table[message.id](message)
                    if return_message:
                        self.send(return_message)
            else:
                # it is a RemoteTransmissionRequest
                if message.id in self.rtr_handler_table:
                    # And we are setup to process it...
                    return_message = \
                        self.rtr_handler_table[message.id](message)
                    if return_message:
                        self.send(return_message)
        elif message is None and self.timeout_function:
            self.timeout_function()

        # run all of the registered iteration functions, one at a time
        # if any generate a message, send it
        for func in self.iteration_function:
            message = func()
            if message:
                self.send(message)
