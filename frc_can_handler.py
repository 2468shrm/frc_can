
import board
import digitalio
import canio

class CANHandler:
    def __init__(self, rx=board.CAN_RX, tx=board.CAN_TX,
                 matches=[],
                 baudrate=1000000, timeout=0.01):
        self.timeout = timeout
        self.rx = rx
        self.tx = tx
        self.baudrate = baudrate
        self.matches = matches
        self.iteration_function = None
        # A table for mapping canio.Messages to a handler function
        self.handler_table = {}
        # A table for mapping canio.RemoteTransmissionRequest to a handler function
        self.rtr_handler_table = {}

        self.can = canio.CAN(rx=self.rx, tx=self.tx, baudrate=self.baudrate)
        self.listener = self.can.listen(matches=self.matches, timeout=self.timeout)
        
        # If the CAN transceiver has a standby pin, bring it out of standby mode
        if hasattr(board, 'CAN_STANDBY'):
            self.standby = digitalio.DigitalInOut(board.CAN_STANDBY)
            self.standby.switch_to_output(False)

        # If the CAN transceiver is powered by a boost converter, turn on its supply
        # For example, the Adafruit M4 CAN Feather Express has a 3.3V to 5V boost
        # converter that powers the CAN transceiver.
        if hasattr(board, 'BOOST_ENABLE'):
            self.boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
            self.boost_enable.switch_to_output(True)

    def send(self, msg):
        """Sends a message. Typically used for status transmissions."""
        self.can.send(msg)
        
    def register_handler(self, message_id, function):
        """Adds a function (handler) to process a message. These are added
        to a dict with message_id as key, function reference as value.
        When a message arrives, if a handler is registered, it is called."""
        if message_id in self.handler_table:
            print(f"ERROR: Attempting to add MessageID that was pre-registered")
            return
        self.handler_table[message_id] = function

    def register_rtr_handler(self, message_id, function):
        """Adds a function (handler) to process a message. These are added
        to a dict with message_id as key, function reference as value.
        When a message arrives, if a handler is registered, it is called."""
        if message_id in self.rtr_handler_table:
            print(f"ERROR: Attempting to add MessageID that was pre-registered")
            return
        self.rtr_handler_table[message_id] = function

    """Example handler for RemoteTransmissionRequest handling.
    def example_rtr_handler(message):
        reply_data = struct.pack(format, source_of_data)
        reply_message = canio.Message(id=message.id,
                                      data=reply_data,
                                      extended=message.extended)
        can_handler.send(reply_message)
    """

    def set_timeout(self, timeout):
        """Be able to change the timeout following constructor."""
        self.timeout = timeout

    def register_iteration(self, iteration_function):
        """Setup a function to be called when a CAN message does not
        arrive.  Examples include sampling and processing I/Os for
        indexing, reading sensors over I2C/SPI, etc."""
        self.iteration_function = iteration_function
    
    def step(self):
        """Wait for the arrival of a message or a timeout. The message
        can be a Message or a RemoteTransmissionRequest.  If one arrives,
        process it. Whether a message/RTR arrives or not, call the
        "iteration" function make progress on processing things needed."""
        message = self.listener.receive()
        if message:
            # A CAN message was received...
            if isinstance(message, canio.Message):
                # it is a canio.Message..
                if message.id in self.handler_table:
                    # And we are setup to process it...
                    self.handler_table[message.id](message)
            else:
                # it is a canio.RemoteTransmissionRequest
                if message.id in self.rtr_handler_table:
                    # And we are setup to process it...
                    self.rtr_handler_table[message.id](message)
        self.iteration_function()
