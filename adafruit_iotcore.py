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
import gc
import time

# required for get_local_time
import rtc
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket


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

    :param dict secrets: Secrets.py file from CIRCUITPY drive.
    :param esp: esp32spi object
    :param bool debug: Enable library debugging, defaults to False.
    """

    def __init__(self, secrets, esp, debug=False):
        self._debug = debug
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
        # Set Time
        self._esp = esp
        requests.set_socket(socket, self._esp)
        self.get_local_time()
        # TODO: create the JWT
        # https://cloud.google.com/iot/docs/how-tos/credentials/jwts#iot-core-jwt-python
        self.create_jwt()

    def connect(self, registry):
        """Connects to the MQTT bridge and authenticates.
        Needs to be performed after create_jwt is executed.
        :param dict registry: The project id, cloud region, registry id,
                                and device id, as a dictionary of strings.
        """
        client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
            registry["project_id"],
            registry["cloud_region"],
            registry["registry_id"],
            registry["device_id"],
        )
        print("Device client_id is '{}'".format(client_id))

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
            response = requests.get(api_url)
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

    # TODO: This requires CircuitPython_RSA, which is in-progress
    def create_jwt(algorithm="RS256", token_ttl="43200"):
        """Creates a JWT (https://jwt.io) to establish an MQTT connection.
            Args:
            project_id: The cloud project ID this device belongs to
            private_key_file: A path to a file containing either an RSA256 or
                    ES256 private key.
            algorithm: The encryption algorithm to use. Only 'RS256' is supported
                        in this implementation.
            Returns:
                A JWT generated from the given project_id and private key, which
                expires in 20 minutes. After 20 minutes, your client will be
                disconnected, and a new JWT will have to be generated.
            Raises:
                ValueError: If the private_key_file does not contain a known key.
            """
        if self._debug:
            print("Creating JWT...")
        # Epoch_offset is needed because micropython epoch is 2000-1-1 and unix is 1970-1-1. Adding 946684800 (30 years)
        epoch_offset = 946684800
        token = {
            # The time the token was issued at.
            "iat": time.time() + epoch_offset,
            # The time the token expires.
            "exp": time.time() + epoch_offset + token_ttl,
            # The audience field should always be set to the GCP project id.
            "aud": self._secrets["project_id"],
        }
        # TODO: Read and set the private key via call to rsa.PrivateKey
        print(
            "Creating JWT using {0} from private key: {1}".format(
                algorithm, self._secrets["private_key"])
            )
        # RSA-based JWT Key Header
        header = { "alg": "RS256", "typ": "JWT" }
        # content = b42_urlsafe_encode(ujson.dumps(header).encode('utf-8'))
        # content = content + '.' + b42_urlsafe_encode(ujson.dumps(claims).encode('utf-8'))
        # signature = b42_urlsafe_encode(rsa.sign(content,private_key,'SHA-256'))
        # return content+ '.' + signature #signed JWT


    def refresh_jwt(self):
        """Refreshes the JWT token if token is nearing expiration.
        https://cloud.google.com/iot/docs/how-tos/credentials/jwts, Refreshing JWTs
        """
        return True
