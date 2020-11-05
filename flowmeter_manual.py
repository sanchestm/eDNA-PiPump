#!/usr/bin/python3

###/home/pi/gps_loc.py
##sudo nano /home/pi/.bashrc

import RPi.GPIO as GPIO
import time, sys
from datetime import datetime, timedelta


while 1:
    try:
        from Adafruit_IO import Client, RequestError, Feed
        ADAFRUIT_IO_KEY = 'aio_vwJZ51l05wBYBNvRppvnKMkcKEjl'
        ADAFRUIT_IO_USERNAME = 'thiagoms'
        aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
        break
    except:
        pass


print('flowmeter connected to intenet')
## import feeds
flow_instant = aio.feeds('test')
total_flow = aio.feeds('totalliters')
fot = aio.feeds('flow-over-time')
pumpstatus = aio.feeds('pumpstatus')


inpt = 22
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inpt, GPIO.IN)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inpt, GPIO.IN, pull_up_down = GPIO.PUD_UP) #PUD_UP
rate_count = 0
tot_count = 0
minutes = 0
constant = 1380
time_new = 0.0
flow_avg = 0
flow_avg2 = 0
global count
count = 0
global long_term_count
long_term_count = 0
delta = 3.5

pwmPin = 12
GPIO.setup(pwmPin, GPIO.OUT)
pwm = GPIO.PWM(pwmPin, 7)
GPIO.cleanup(pwmPin)
GPIO.setwarnings(False)



def countPulse(channel):
   global count
   global long_term_count
   count += 1
   long_term_count += 1


GPIO.add_event_detect(inpt, GPIO.FALLING, callback=countPulse) #GPIO.FALLING

print('Time         ', '\t', time.asctime(time.localtime()))
starttime = datetime.now()
#working_hours = [starttime + timedelta(hours=n) for n in range(24)]

#running for the number of cycles
while 1:
    while aio.receive(pumpstatus.key).value == 'IDLE':
        future = time.time() + delta
        while time.time() <= future:
            try:
                pass
            except KeyboardInterrupt:
                print('exited')
                pwm.stop()
                GPIO.cleanup(pwmPin)
                GPIO.cleanup()
                sys.exit()
    long_term_count = 0
    #print(current_hour)
    aio.send_data(flow_instant.key, 0)
    aio.send_data(total_flow.key, 0)
    GPIO.setup(pwmPin, GPIO.OUT)
    dutyCycle = 50
    pwm.start(dutyCycle)
    aio.send_data(pumpstatus.key, 'RUNNING')
    print('Started Time         ', '\t', time.asctime(time.localtime()))
    pwm.ChangeDutyCycle(90)
    #pumping for 10min of the hour
    while aio.receive(pumpstatus.key).value == 'RUNNING':  ##10 minutes
        #### output the pwm to velocimeter
        ### reset timer
        future = time.time() + delta
        rate_count = 0
        count = 0
        ### loop to count flowmeter frequency
        while time.time() <= future:
            try:
                pass
                #print('\rmL/min {:10d} -  state {:1d} '.format(round(flow_avg2,2), GPIO.input(inpt)), end = '')
            except KeyboardInterrupt:
                print('exited')
                pwm.stop()
                GPIO.cleanup(pwmPin)
                GPIO.cleanup()
                time.sleep(.25)
                sys.exit()
        flow_avg2 = (count/delta)/constant*1000*60
        if (flow_avg2 <= 10): dutyCycle = 10
        elif (flow_avg2 >= 2000): dutyCycle = 20
        if (flow_avg2 <= 500) & (dutyCycle > 0): dutyCycle -= 5
        elif (flow_avg2 >= 500) & (dutyCycle < 100): dutyCycle += 5
        pwm.ChangeDutyCycle(dutyCycle)
        aio.send_data(flow_instant.key, round(flow_avg2,2) )
        aio.send_data(total_flow.key, round(long_term_count/constant, 2) )
    pwm.stop()
    GPIO.cleanup(pwmPin)
    aio.send_data(pumpstatus.key, 'IDLE')
    aio.send_data(flow_instant.key, 0)
    aio.send_data(total_flow.key, round(long_term_count/constant, 2) )
    aio.send_data(fot.key,  round(long_term_count/constant, 2) )
    print('Stopped Time         ', '\t', time.asctime(time.localtime()))
    print('Total Flow:          ' + str(long_term_count/constant/60))
    print('Cycle number         ' + str(long_term_count))
    with open('/home/pi/Desktop/Log.txt', 'a+') as f:
        f.write('Time {} - flow(L) {:4f}\n'.format( time.asctime(time.localtime()), long_term_count/constant/60 ))


GPIO.cleanup()
