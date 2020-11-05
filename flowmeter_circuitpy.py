from adafruit_circuitplayground import cp

import time, sys

from Adafruit_IO import Client, RequestError, Feed
ADAFRUIT_IO_KEY = 'aio_vwJZ51l05wBYBNvRppvnKMkcKEjl'
ADAFRUIT_IO_USERNAME = 'thiagoms'
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

flow_instant = aio.feeds('test')



GPIO.setmode(GPIO.BOARD)
inpt = 22
GPIO.setup(inpt, GPIO.IN)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inpt, GPIO.IN, pull_up_down = GPIO.PUD_UP)
rate_count = 0
tot_count = 0
minutes = 0
constant = 38
time_new = 0.0
flow_avg = 0
flow_avg2 = 0
global count
count = 0

def countPulse(channel):
   global count
   count += 1

GPIO.add_event_detect(inpt, GPIO.FALLING, callback=countPulse)

print('Time         ', '\t', time.asctime(time.localtime()))
while True:
    future = time.time() + 2.5
    rate_count = 0
    count = 0
    while time.time() <= future:
        try:
            print('\rmL/min {:10d} -  state {:1d}'.format(round(2*flow_avg2/2.5,2), GPIO.input(inpt)), end = '')
        except KeyboardInterrupt:
            print('exited')
            GPIO.cleanup()
            sys.exit()
    flow_avg2 = round(count/constant)*60
    aio.send_data(flow_instant.key, round(2*flow_avg2/2.5,2) )
    with open('/home/pi/Desktop/Log.txt', 'a+') as f:
        f.write('Time {} - flow(mL/min) {:10d}\n'.format( time.asctime(time.localtime()), round(2*flow_avg2/2.5,2)))

print('exited')
GPIO.cleanup()
