#!/usr/bin/python3


#sudo nano /home/pi/.bashrc

import serial
import pynmea2
import time, sys
while 1:
    try:
        from Adafruit_IO import Client, RequestError, Feed
        from Adafruit_IO import MQTTClient
        ADAFRUIT_IO_KEY = 'aio_vwJZ51l05wBYBNvRppvnKMkcKEjl'
        ADAFRUIT_IO_USERNAME = 'thiagoms'
        aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
        break
    except:
        pass

#### sudo chmod a+rw /dev/ttyACM0
#### scp ~/Documents/RPIzero/gps_loc.py pi@192.168.43.181:~/

print('gps connected to internet')
gps_feed = aio.feeds('gps')

port = "/dev/ttyACM0"
#port = "/dev/serial0"
counter = 0

def parseGPS(val, new):
    if val.find('GGA') > 0:
        msg = pynmea2.parse(val)
        #print ("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s -- Satellites: %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units,msg.num_sats))
        aio.send_data(gps_feed.key, new , metadata = { 'lat': float(msg.latitude) , 'lon':  float(msg.longitude), 'ele':float(msg.altitude), 'created_at':time.asctime(time.gmtime()) } )

serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
while True:
    line = serialPort.readline()
    try:
        parseGPS(line.decode("utf-8"), counter)
    except:
        pass #print('gps not fixed yet')
    counter += 1
    time.sleep(15)
