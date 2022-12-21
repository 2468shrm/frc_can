# frc_can

## What is frc_can?

A simple python-based wrapper around the canio module for connecting CAN-connected
sensors to FRC robots. It is intended to simplify application creation. It runs on
Adafruit feather boards running circuitpython, specifically the M4 CAN Express
Feather board.

NOTE: This code is experimental. Use at own risk.

## How does it help?

There are two objects provided: FRCCANDevice (in frc_can.py) and CANHandler (in frc_can_handler.py). There is a third object provided, CANCarrierBoard, that
supplements the board attributes of the circuitpython builtins on their boards
and defines mappings when using an M4 CAN Express Feather Board with a 2468 CAN
Carrier Board.

# FRCCANDevice
FRCCANDevice provides basic FRC CAN protocol assistance, specifically MessageID
field construction and field value enumeration (defined values to fields).
FRCCANDevice is used by CANHandler.

# CANHandler
CANHandler assists in creating applications by providing a framework to associate
received messages (Message or RemoteTransmissionRequest) to functions. CANHander
also provides a means to call a data function after processing a message or
following a listener timeout.

# Using CANHandler In An Embedded Application

## Message and RemoteTranser Request filter create
Create a list of canio.Match objects for the canio.CAN.listen.receive function.
These are the message IDs to be filtered out and returned. The IDs may be
for canio.Messages or canio.RemoteTransferRequests. Note that not supplying a list (i.e. passing None) causes all messages to be received (no filtering).

`[canio.Match(id: int, *, mask: Optional[int] = None, extended: bool = False)]`

## Create a CANHandler object
x

`CANHandler(matches: Union([canio.Match(id: int, *, mask: Optional[int] = None, extended: bool = False)], None), timeout: float=0.01)`


## Register a function to run when a MessageID or RemoteTransmissionRequest is received

Messages typically have some form of message-specific action. Therefore, in this wrapper
messages are associated with a function. The register_handler() and register_rtr_handler()
methods maintain internal dictionaries to associate the id with function called when an id
is received. Note that the iteration function is called immediately after processing a
recieved message or after a timeout when no message is received.

Example

`register_handler(message_id: int, function: function)`

Call this for every function/message id mapping.

## Register a function to run each iteration step
The iteration function is a function that handles non-CAN-related operations of a
sensor application. For example reading a sensor, performing computation based
on sensor reading, and/or updating status LEDs.

`register_iteration(iteration_function: function)`


## Periodically call the step method

After the above is complete, the run() method is called periodically.


# Example

```
from frc_can import FRCCANDevice
from frc_can_handler import CANHandler
from can_carrier_board import CANCarrierBoard
from robot_signal_light import RSL

# create a robot signal light (RSL object)
rsl = RSL(pin=CANCarrierBoard.NEOPIXEL, num_pixels=16)

# Messages to listen to.. are heartbeat messages sent by the roboRIO
# WPILib heartbeat message ID (see
# https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html)
HEARTBEAT = FRCCANDevice()
HEARTBEAT.update(0x01011840)

messageid_match_list = [canio.Match(id=HEARTBEAT.message_id, extended=True)]

can_handler = CANHandler(matches=messageid_match_list, timeout=0.01)
can_handler.register_handler(message_id=HEARTBEAT.message_id, function=rsl.can_heartbeat_message)
can_handler.register_iteration(rsl.iterate)

while True:
    can_handler.step()
```
