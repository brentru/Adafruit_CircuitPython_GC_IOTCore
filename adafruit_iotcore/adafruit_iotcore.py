# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modified by Brent Rubell for Adafruit Industries, 2019
"""
`adafruit_cloud_iot_core`
================================================================================

Google Cloud IOT Core Access from CircuitPython MQTT


* Author(s): Brent Rubell

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
# Core CircuitPython modules
import gc
import time
import rtc
import json

import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

from adafruit_rsa import PrivateKey, sign
from adafruit_iotcore.tools import string


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Cloud_IOT_Core.git"

TIME_SERVICE = (
    "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s"
)
# our strftime is %Y-%m-%d %H:%M:%S.%L %j %u %z %Z see http://strftime.net/ for decoding details
# See https://apidock.com/ruby/DateTime/strftime for full options
TIME_SERVICE_STRFTIME = (
    "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"
)

class Cloud_Core:
    """CircuitPython Google Cloud IoT Core implementation.

    :param NetworkManager: Network Manager module, such as WiFiManager.
    :param dict secrets: Secrets.py file from CIRCUITPY.
    :param bool debug: Enable library debugging, defaults to False.
    """

    def __init__(self, network_manager, secrets, debug=False):
        self._debug = debug
        network_manager_type = str(type(network_manager))
        if 'ESPSPI_WiFiManager' in network_manager_type:
            self._wifi = network_manager
        else:
            raise TypeError("This library requires a NetworkManager object.")
        if hasattr(secrets, "keys"):
            self._secrets = secrets
        else:
            raise AttributeError(
                "Project settings are kept in secrets.py, please add them there!"
            )
        # Cloud IOT Core Configuration
        self._proj_id = secrets["project_id"]
        self._region = secrets["cloud_region"]
        self._reg_id = secrets["registry_id"]
        self._device_id = secrets["device_id"]
        self._private_key = secrets["private_key"]
        # Set RTC Network Time
        self.get_local_time()
        # Generate JWT
        # self.create_jwt()


    def get_local_time(self):
        """Fetch and "set" the local time of this microcontroller to the local time at the location, using an internet time API.
        from Adafruit IO Arduino
        """
        api_url = None
        try:
            aio_username = self._secrets["aio_username"]
            aio_key = self._secrets["aio_key"]
        except KeyError:
            raise KeyError(
                "\n\nOur time service requires a login/password to rate-limit. Please register for a free adafruit.io account and place the user/key in your secrets file under 'aio_username' and 'aio_key'"
            )
        location = None
        location = self._secrets.get("timezone", location)
        if location:
            if self._debug:
                print("Getting time for timezone", location)
            api_url = (TIME_SERVICE + "&tz=%s") % (aio_username, aio_key, location)
        else:  # we'll try to figure it out from the IP address
            print("Getting time from IP address")
            api_url = TIME_SERVICE % (aio_username, aio_key)
        api_url += TIME_SERVICE_STRFTIME
        try:
            response = self._wifi.get(api_url)
            if self._debug:
                print("Time request: ", api_url)
                print("Time reply: ", response.text)
            times = response.text.split(" ")
            the_date = times[0]
            the_time = times[1]
            year_day = int(times[2])
            week_day = int(times[3])
            is_dst = None  # no way to know yet
        except KeyError:
            raise KeyError(
                "Was unable to lookup the time, try setting secrets['timezone'] according to http://worldtimeapi.org/timezones"
            )  # pylint: disable=line-too-long
        year, month, mday = [int(x) for x in the_date.split("-")]
        the_time = the_time.split(".")[0]
        hours, minutes, seconds = [int(x) for x in the_time.split(":")]
        now = time.struct_time(
            (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
        )
        rtc.RTC().datetime = now
        if self._debug:
            print("current time: {}".format(time.localtime()))

        # now clean up
        response.close()
        response = None
        gc.collect()
