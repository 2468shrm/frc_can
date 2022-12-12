
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
        self.matches = matches
        self.iteration_function = None
        self.can_status_message_id = None
        self.handler_table = {}
        self.can = canio.CAN(rx=rx, tx=tx, baudrate=baudrate)
        self.listener = self.can.listen(matches=self.matches, timeout=self.timeout)
        # If the CAN transceiver has a standby pin, bring it out of standby mode
        if hasattr(board, 'CAN_STANDBY'):
            self.standby = digitalio.DigitalInOut(board.CAN_STANDBY)
            self.standby.switch_to_output(False)

        # If the CAN transceiver is powered by a boost converter, turn on its supply
        if hasattr(board, 'BOOST_ENABLE'):
            self.boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
            self.boost_enable.switch_to_output(True)

    def send(self, msg):
        self.can.send(msg)
        
    def register_handler(self, message_id, function):
        if message_id in self.handler_table:
            print(f"ERROR: Attempting to add MessageID that was pre-registered")
            return
        self.handler_table[message_id] = function

    def set_timeout(self, timeout):
        self.timeout = timeout

    def register_iteration(self, iteration_function):
        self.iteration_function = iteration_function
    
    def register_can_status_send(self, can_status_message_id):
        self.can_status_message_id = can_status_message_id

    def step(self):
        # wait 0.01s for the arrival of a message.. if one
        # arrives, process it, otherwise call the ball counter
        # read function.
        message = self.listener.receive()
        if message:
            # A CAN message was received...
            if message.id in self.handler_table:
                # And we are setup to process it...
                self.handler_table[message.id](message)
        else:
            self.iteration_function()
