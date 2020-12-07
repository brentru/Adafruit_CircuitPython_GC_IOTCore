Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-iotcore/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/iotcore/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_IOTCore.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_IOTCore
    :alt: Build Status

Google Cloud IOT Core for CircuitPython.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Adafruit CircuitPython JWT <https://github.com/adafruit/Adafruit_CircuitPython_JWT>`_
* `Adafruit CircuitPython Logging <https://github.com/adafruit/Adafruit_CircuitPython_Logger>`_


Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
=====================
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!


On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-iotcore/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-iotcore

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-iotcore

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-iotcore

Usage Example
=============

Usage example within examples/ folder.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_IOTCore/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

License
=======

This library was written by Google for MicroPython. We've converted it to
work with CircuitPython and made changes so it works with boards supported by
CircuitPython and the CircuitPython API.

We've added examples for using this library to transmit board telemetry data along
with sensor data to Google's Cloud Platform.

This open source code is licensed under the Apache license (see LICENSE) for details.
