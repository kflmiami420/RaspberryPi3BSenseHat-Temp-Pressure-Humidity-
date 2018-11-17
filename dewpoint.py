#!/usr/bin/env python2.7

from sense_hat import SenseHat
sense = SenseHat()
sense.clear()
print 'Press Ctrl-C to quit.'

    tempc = sense.get_temperature()
    tempc = round(tempc, 1)
    temp = sense.get_temperature()
    temp = round(temp, 1)
    temp = ((temp / 5) * 9) + 32  # Convert to Farhenheit
    humidity = sense.get_humidity()
    humidity = round(humidity, 1)
    pressure = sense.get_pressure()
    pressure = round(pressure, 1)

    TD = 243.04 * (math.log(humidity / 100) + ((17.625 * tempc) / (243.04 + tempc))) / (
    17.625 - math.log(humidity / 100) - ((17.625 * tempc) / (243.04 + tempc)))
    TD = round(TD, 1)
    
    print "Temp (F): ", temp
    print "Humidity: ", humidity
    print "DewPoint: ", TD
    print "Pressure: ", pressure, "\n"
    time.sleep(2)
