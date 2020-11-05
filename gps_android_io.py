import RPi.GPIO as GPIO
import time, sys
from Adafruit_IO import Client, RequestError, Feed
ADAFRUIT_IO_KEY = 'aio_vwJZ51l05wBYBNvRppvnKMkcKEjl'
ADAFRUIT_IO_USERNAME = 'thiagoms'
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
