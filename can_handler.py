
import board
import digitalio
import busio
from canio import Message


class CANHandler:
    def __init__(self, carrier_board, drain_queue=False) -> None:
        """CANHandler provides a convenient framework for building robotics
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

        # A table for mapping Messages to a handler function
        self.handler_table = {}

        # A table for mapping RemoteTransmissionRequest to a
        # handler function
        self.rtr_handler_table = {}

        # A table for mapping a function that may optionally be called
        # if there is no matching message received (i.e. receive returns
        # None). Optional being that if self.unmatched_handler is not
        # None, it gets called.
        self.unmatched_handler = None

        # Functions run each iteration step
        self.iteration_handler = None

        # an optional timeout function that can be run, but only if
        # set and a message is not received in timeout period
        self.timeout_handler = None

    def register_msg_handler(self, message_id, function) -> None:
        """Adds a function (handler) to process a specific CAN message.
        These are added to a dict with message_id as key, function
        reference as value. When a message arrives, if a handler is
        registered, it is called."""
        if message_id in self.handler_table:
            print("ERROR: Attempting to add MessageID that was"
                  " pre-registered")
            return
        self.handler_table[message_id] = function

    def register_rtr_handler(self, message_id, function) -> None:
        """Adds a function (handler) to process a message. These are added
        to a dict with message_id as key, function reference as value.
        When a message arrives, if a handler is registered, it is called."""
        if message_id in self.rtr_handler_table:
            print("ERROR: Attempting to add MessageID that was "
                  "pre-registered")
            return
        self.rtr_handler_table[message_id] = function

    def register_unmatched_handler(self, function) -> None:
        """Adds a function (handler) to process if a Message or RTR is received
        that does not match the expected list"""
        self.unmatched_handler = function

    def register_timeout_handler(self, function) -> None:
        """Adds a function (handler) to call in the event that a CAN
        message was not receive during the timeout period. The idea is to
        use this to detect a missing heartbeat message."""
        self.timeout_handler = function

    def register_iteration_handler(self, iteration_function) -> None:
        """Setup a function to be called when a CAN message does not
        arrive. Examples include sampling and processing I/Os for
        indexing, reading sensors over I2C, SPI, etc."""
        if isinstance(iteration_function, list):
            self.iteration_function = iteration_function
        else:
            # store as a list, even a single entry list
            self.iteration_function = [iteration_function]

    def step(self) -> None:
        """Wait for the arrival of a message or a timeout. The message
        can be a Message or a RemoteTransmissionRequest. If one arrives,
        process it. Whether a message/RTR arrives or not, call the
        "iteration" function make progress on processing things needed."""
        message = self.cb.listener.receive()
        if message:
            while self.cb.listener.in_waiting():
                # A CAN message was received...
                if isinstance(message, Message):
                    # it is a Message..
                    if message.id in self.handler_table:
                        # And we are setup to process it...
                        return_message = (
                            self.handler_table[message.id](message)
                        )
                        if return_message:
                            self.cb.can.send(return_message)
                    # if there is a handler registered for non-matching
                    # msg, call it
                    elif self.unmatched_handler:
                        self.unmatched_handler(message)
                else:
                    # it is a RemoteTransmissionRequest
                    if message.id in self.rtr_handler_table:
                        # And we are setup to process it...
                        return_message = \
                            self.rtr_handler_table[message.id](message)
                        if return_message:
                            self.cb.can.send(return_message)
                    # if there is a handler registered for non-matching msg,
                    # call it
                    elif self.unmatched_handler:
                        self.unmatched_handler(message)
                # Leave loop after one iteration if drain_queue is false OR
                # there is no more messages in the queue.  Otherwise,
                # continue draining..
                if self.drain_queue is False and self.cb.listener.in_waiting():
                    break
                # get next message
                message = self.cb.listener.receive()

        # No message received (ot tiemd out) and a timeout
        elif message is None and self.timeout_handler:
            self.timeout_handler(message)

        # run all of the registered iteration functions, one at a time
        # if any generate a message, send it
        if self.iteration_handler:
            for func in self.iteration_handler:
                _message = func()
                if _message:
                    self.cb.can.send(_message)
