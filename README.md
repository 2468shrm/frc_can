# frc_can

## What is frc_can?

A simple circuitpython-based wrapper around the canio module for connecting
CAN-connected sensors to FRC robots. It is intended to simplify the creation of
FRC sensor and other applications. It runs on Adafruit feather boards running
circuitpython, specifically the M4 CAN Express Feather board.

NOTE: This code is experimental. Use at own risk.

## How does it help?

There are three objects provided: *FRCCANDevice* (in frc_can.py), *CANHandler* (in frc_can_handler.py), and *CANCarrierBoard* (in can_carrier_board.py). 

## FRCCANDevice
FRCCANDevice provides basic FRC CAN protocol assistance, specifically MessageID
field construction and field value enumeration (defined values to fields).
FRCCANDevice is used by CANHandler.

## CANHandler
CANHandler assists in creating applications by providing a framework to associate
received messages (Message or RemoteTransmissionRequest) to functions. CANHander
also provides a means to call a data function after processing a message or
following a listener timeout.

## CANCarrierBoard
Supplements the board attributes of the circuitpython builtins on their boards
and defines mappings when using an
[Adafruit Feather M4 CAN Express](https://www.adafruit.com/product/4759)
board with a
[2468 CAN Carrier Board](https://github.com/2468shrm/M4_CAN_Feather_Carrier_v2).

# APIs Of Each Class

## FRCCANDevice

### Constructor
`FRCCANDevice(int: device_type = 0, int: manufacturer = 0, int: api = 0, int: device_number = 0)`
### update
`FRCCANDevice.update(int: msg_id)`
### update_device_type
`FRCCANDevice.update_device_type(int: device_type)`
### update_manufacturer
`FRCCANDevice.update_manufacturer(int: manufacturer)`
### update_api
`FRCCANDevice.update_api(int: api)`
### update_device_number
`FRCCANDevice.update_device_number(int: device_number)`


## CANHandler

### Constructor
`CANHandler(rx: board.pin, tx: board.pin, matches=list(canio.Match),
int: baudrate, float: timeout)`
### send
`CANHandler.send(canio.Message: msg)`
### register_handler
`CANHandler.register_handler(int: message_id, function: iteration_function)`
### register_rtr_handler
`CANHandler.register_rtr_handler(int: message_id, function: iteration_function)`
### register_iteration
`CANHandler.register_iteration(function: iteration_function)`
### set_timeout
`CANHandler.set_timeout(float: timeout)`
### step
`CANHandler.step()`


## CANCarrierBoard

### Pin Mappings
Example mappings you get from the CANCarrierBoard class:
```
CANCarrierBoard.DIO0      (board attribute for pin digital input 0)
CANCarrierBoard.AI0       (board attribute for pin analog input 0)
CANCarrierBoard.NEOPIXEL  (board attribute for pin NeoPixel data signal)
CANCarrierBoard.SCL0      (board attribute for pin STEMMA QT/Qwiic interface 0 clock signal)
CANCarrierBoard.SDA0      (board attribute for pin STEMMA QT/Qwiic interface 0 data signal)
```

### Constructor
Instantiating a CANCarrierBoard object also (optionally) initializes one of two
board-level features.
 
`CANCarrierBoard(v2: Optional[bool] = False, dio_pull_ups: Optional[bool] = False)`

- If the v2 parameter is set to True, this drives the output enable signal for the
level shifter so the level shifter becomes active.

- If the dio_pull_ups parameter is set to True, the feather board's I/O connected to
the carrier board's DIOs have their internal pull ups enabled.

### enable_level_shifter
`CANCarrierBoard.enable_level_shifter()`
### disable_level_shifter
`CANCarrierBoard.disable_level_shifter()`
### enable_dio_pullup
`CANCarrierBoard.enable_dio_pullup(pin: board.pin)`
### enable_all_dio_pullups
`CANCarrierBoard.enable_all_dio_pullups()`
### set_as_input
`CANCarrierBoard.set_as_input(pin: board.pin)`

# Creating An Embedded Application Using CANHandler
Application creation becomes formulaic.

- A list of message IDs/remote transmit request IDs is defined as the CAN API

- It is advised that a class is created
for the sensor. The sensor class should have a method for initializing the
sensor (using CANCarrierBoard definitions if applicable) and another method
for periodic sensor functions (read, process, etc.) and finally methods for each
of the CAN messages expected to be processed.

- Funtions/methods of the sensor class instance are registered with the CANHandler
object

- The sensor periodic function is registered with the CANHandler object

Finally,
- The CANHandler.step() method is called periodically

## Message and RemoteTranser Request filter creation
Create a list of canio.Match objects for the canio.CAN.listen.receive function.
These are the message IDs to be filtered out and returned. The IDs may be
for canio.Messages or canio.RemoteTransferRequests. Note that not supplying a list (i.e. passing None) causes all messages to be received (no filtering).

`[canio.Match(id: int, *, mask: Optional[int] = None, extended: bool = False)]`

## Create a CANHandler object
The CANHandler object is passed two optional parameters:
- A list of canio.Match objects that define the MsgID/RTRIDs for which the CANHandler will
listen.
- The timeout period for listening to a message.

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

After the above is complete, the step() method is called periodically.


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
