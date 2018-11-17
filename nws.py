#!/usr/bin/env python2.7

import json
import sys
import time
import datetime

# libraries
import sys
import urllib2
import json
import gspread
import math
from oauth2client.client import SignedJwtAssertionCredentials
from sense_hat import SenseHat

# Oauth JSON File
GDOCS_OAUTH_JSON = '/home/pi/Desktop/wps/current/RPiSHatWS-f7779fdfa131.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'RPiMiniWeatherStation'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 10


def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        json_key = json.load(open(oauth_key_file))
        credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                    json_key['private_key'],
                                                    ['https://spreadsheets.google.com/feeds'])
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print 'Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!'
        print 'Google sheet login failed with error:', ex
        sys.exit(1)


sense = SenseHat()
sense.clear()
print 'Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS)
print 'Press Ctrl-C to quit.'
worksheet = None
while True:
    # Login if necessary.
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    # Attempt to get sensor reading.
    tempc = sense.get_temperature()
    tempc = round(tempc, 1)
    temp = sense.get_temperature()
    temp = round(temp, 1)
    temp = ((temp / 5) * 9) + 32  # Convert to Farhenheit
    humidity = sense.get_humidity()
    humidity = round(humidity, 1)
    pressure = sense.get_pressure()
    pressure = round(pressure, 1)

    # Calculate Dew Point
    TD = 243.04 * (math.log(humidity / 100) + ((17.625 * tempc) / (243.04 + tempc))) / (
    17.625 - math.log(humidity / 100) - ((17.625 * tempc) / (243.04 + tempc)))
    TD = round(TD, 1)

    # Get orientation
    acceleration = sense.get_accelerometer_raw()
    x = acceleration['x']
    y = acceleration['y']
    z = acceleration['z']

    x = round(x, 0)
    y = round(y, 0)
    z = round(z, 0)

    print("x={0}, y={1}, z={2}".format(x, y, z))

    if x == -1:
        sense.set_rotation(90)
    elif y == 1:
        sense.set_rotation(0)
    elif y == -1:
        sense.set_rotation(180)
    else:
        sense.set_rotation(270)

    # Attempting to Create Background color based on temp
    if temp > 20 and temp < 60:
        bg = [0, 0, 155]  # blue
    if temp > 61 and temp < 70:
        bg = [0, 155, 0]  # Green
    if temp > 71 and temp < 80:
        bg = [155, 155, 0]  # Yellow
    if temp > 81 and temp < 90:
        bg = [255, 127, 0]  # Orange
    if temp > 91 and temp < 100:
        bg = [155, 0, 0]  # Red
    if temp > 101 and temp < 110:
        bg = [255, 0, 0]  # Bright Red
    if temp > 111 and temp < 120:
        bg = [155, 155, 155]  # White

    # 8x8 RGB
    sense.clear()
    info = 'Temp. F ' + str(temp) + 'Temp. C ' + str(tempc) + 'Hum. ' + str(humidity) + 'Press. ' + str(
        pressure) + 'DewPoint' + str(TD)
    sense.show_message(info, scroll_speed=0.10, back_colour=bg, text_colour=[155, 155, 155])

    # Print
    print "Temp (F): ", temp
    print "Temp (C): ", tempc
    print "Humidity: ", humidity
    print "DewPoint: ", TD
    print "Pressure: ", pressure, "\n"

    # Append the data in the spreadsheet, including a timestamp
    try:
        worksheet.append_row((datetime.datetime.now(), temp, tempc, humidity, TD, pressure))
    except:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print 'Append error, logging in again'
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait 5 seconds before continuing
    print 'Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME)
    time.sleep(FREQUENCY_SECONDS)
