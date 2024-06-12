# frc_can

## What is frc_can?

A simple circuitpython-based module for creating CAN-based FRC applications.
It is built around the canio module and useful for connecting smart sensors
connected to single-board computers allowing us to make CAN-connected sensors
for FRC robots. It is intended to simplify the creation of FRC sensor and
other applications. It runs on Adafruit feather boards running circuitpython,
specifically the M4 CAN Express Feather board.

NOTE: This code is experimental. Use at own risk.

## How does it help?

There are multiple objects provided:
  - *FRCCANDevice* (in ids/msg_format.py)
  - *HeartBeatMsg* (in ids/heartbeat.py)
  - *CANHandler* (in can_handler.py)
  - *CANCarrierBoard* (in carrier_board/*board*.py, where board=m4_feather_can,
  raspberrypi_pico_w, etc.). 

## FRCCANDevice
FRCCANDevice provides basic FRC CAN message object formatting assistance. FRC has a
defined MessageID field partition and field values.

## CANHandler
CANHandler assists in creating applications by providing a framework to associate
received messages (Message or RemoteTransmissionRequest) to functions. CANHander
also provides a means to call a data function after processing a message or
following a listener timeout.

## CarrierBoard
Supplements the board attributes found in the circuitpython builtins on the
Adafruit boards and defines mappings when using an
[Adafruit Feather M4 CAN Express](https://www.adafruit.com/product/4759)
board with a
[2468 CAN Carrier Board](https://github.com/2468shrm/M4_CAN_Feather_Carrier_v2).
or a [Raspberry Pi Pico W](https://www.adafruit.com/product/5526) board with its
carrier board (link to come).

# APIs Of Each Class

## FRCCANDevice
### Importing
`from ids.msg_format import FRCCANDevice`

### Constructor
`FRCCANDevice(int: device_type=None, int: manufacturer=None, int: api=None, int: device_number=None, message_id=None)`

Plus getter and setter functions for device_type, manufacturer, api, device_id, 
and message_id.  A __str__ function is provided for debugging.

## HearBeatMsg
THe HeartBeatMsg class is used for creating, inserting, extracting,
and inspecting the fields and content of the CAN message payload for
a heart beat message.

### Importing
`from ids.heartbeat import HeartBeatMsg`
### Constructor
`HeartBeatMsg(int: data=None)`

Use data=value to initialize a known heart beat message for debugging.
Otherwise, there is getter/setter functions for each field in the
heart beat message payload. This includes:
- data (gets/sets the whole payload data (an bytearray of length 8 bytes))
- match_time
- match_number
- replay_number
- red_alliance
- enabled
- autonomous
- test_mode
- system_watchdog
- tournament_type
- time_of_day_yr
- time_of_day_month
- time_of_day_day
- time_of_day_sec
- time_of_day_min
- time_of_day_hr

There is also a convenient function id() which returns the message id of
a heart beat message.

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

## CarrierBoard

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
 
`CANCarrierBoard(configuration)`

Configuration is a dict() that contains a number of defined key/values
specific to the target carrier board.

#### m4_feather_can configuration dict definition
The key values and values include:
- include_can : False | CAN configuration dict() which includes
  - loopback : True | False
  - silent : True | False
  - baudrate : 125_000 | 250_000 | 500_000 | 1_000_999
  - auto_restart : True | False
- incldue_eth : False | Ethernet configuration dict() which includes
  - is_dhcp : True | False
  - mac : "xx:yy:zz:aa:bb:cc"
  - hostname : str
  - debug : True | False
- include_microsd : True | False
- init_i2c0 : True | False
- init_i2c1 : True | False
- init_i2c2 : True | False
- init_neopixel : False | neopixel configuration dict() which includes
  - num_pixels : int

An example:
```
# Enable CAN for FRC setup and enable the Neopixel interface with a
# single pixel, but nothing else.
#
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

# Initialize the carrier board
cb = CarrierBoard(CarrierBoardConfiguration)
```

### set_as_input
`CANCarrierBoard.set_as_input(pin: board.pin)`

# Creating An Embedded Application Using CANHandler

*OUTDATED.. NEEDS UPDATE*



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
