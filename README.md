# CircuitPythonDynamixel

# Introduction
A user friendly API to interface with Dynamixel servos.

# Dependencies
Everything should be part of the standard circuitpython lib
  * digitalio
  * board
  * busio

# Getting Started
This is designed for [Adafruit Metro ESP32-S3](https://learn.adafruit.com/adafruit-metro-esp32-s3). A HAT that supports out of the box UART and power with only a single cable is also available [here](https://github.com/dbd/AdafruitMetroESP32-DynamixelHat/tree/main).

Copy the dynamixel folder to `lib/` on your CircuitPython board. If you are short on space then copy all the files in `dynamixel/` and only copy the devices that you are using.

# Usage Example

```python
import time
from dynamixel.devices import XL430_W250_T
m = XL430_W250_T('roll', 1)
n = XL430_W250_T('pitch', 2)
o = XL430_W250_T('yaw', 3)
while True:
    m.ledOff()
    n.ledOff()
    o.ledOff()
    time.sleep(.5)
    m.ledOn()
    n.ledOn()
    o.ledOn()
    time.sleep(.5)
```

# Contributing
Feel free to raise a PR to add a device and make sure that all features in the base class are covered if applicable.
