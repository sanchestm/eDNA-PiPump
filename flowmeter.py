import RPi.GPIO as GPIO
import time, sys
from datetime import datetime, timedelta
from Adafruit_IO import Client, RequestError, Feed


ADAFRUIT_IO_KEY = 'aio_vwJZ51l05wBYBNvRppvnKMkcKEjl'
ADAFRUIT_IO_USERNAME = 'thiagoms'
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)


## import feeds
flow_instant = aio.feeds('test')
total_flow = aio.feeds('totalliters')
fot = aio.feeds('flow-over-time')
pumpstatus = aio.feeds('pumpstatus')



GPIO.setmode(GPIO.BOARD)
inpt = 22
GPIO.setup(inpt, GPIO.IN)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inpt, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #PUD_UP
rate_count = 0
tot_count = 0
minutes = 0
constant = 38/36.3157
time_new = 0.0
flow_avg = 0
flow_avg2 = 0
global count
count = 0
long_term_count = 0
delta = 2.1
pwmPin = 12


def countPulse(channel):
   global count
   count += 1

GPIO.add_event_detect(inpt, GPIO.RISING, callback=countPulse) #GPIO.FALLING

print('Time         ', '\t', time.asctime(time.localtime()))
starttime = datetime.now()
working_hours = [starttime + timedelta(hours=n) for n in range(24)]

#running for the number of cycles
for current_hour in working_hours:
    long_term_count = 0
    #print(current_hour)
    aio.send_data(flow_instant.key, 0)
    aio.send_data(total_flow.key, 0)
    GPIO.setup(pwmPin, GPIO.OUT)
    pwm = GPIO.PWM(pwmPin, 10)
    dutyCycle = 50
    pwm.start(dutyCycle)
    aio.send_data(pumpstatus.key, 'RUNNING')
    print('Started Time         ', '\t', time.asctime(time.localtime()))
    #pumping for 5min of the hour
    while datetime.now() <= current_hour + timedelta(minutes = 5):  ##10 minutes
        future = time.time() + delta
        rate_count = 0
        count = 0
        while time.time() <= future:
            try:
                pass
                #print('\rmL/min {:10d} -  state {:1d} '.format(round(flow_avg2,2), GPIO.input(inpt)), end = '')
            except KeyboardInterrupt:
                print('exited')
                GPIO.cleanup()
                sys.exit()
        flow_avg2 = (count/delta)/constant*1000
        long_term_count += count
        if (flow_avg2 <= 500) & (dutyCycle >=5): dutyCycle -= 5
        if (flow_avg2 >= 500) & (dutyCycle <=95): dutyCycle += 5
        pwm.ChangeDutyCycle(dutyCycle)
        aio.send_data(flow_instant.key, round(flow_avg2,2) )
        #aio.send_data(total_flow.key, round(long_term_count/constant/60, 2) )
        #if aio.receive(pumpstatus.key).value == 'IDLE': break
        if round(long_term_count/constant, 2) > 4: break

    #pwm.ChangeDutyCycle(0)
    #pwm.stop()
    GPIO.cleanup(12)
    aio.send_data(pumpstatus.key, 'IDLE')
    aio.send_data(flow_instant.key, 0)
    aio.send_data(fot.key,  round(long_term_count/constant/60, 2) )
    print('Stopped Time         ', '\t', time.asctime(time.localtime()))

    with open('/home/pi/Desktop/Log.txt', 'a+') as f:
        f.write('Time {} - flow(L) {:4f}\n'.format( time.asctime(time.localtime()), long_term_count/constant/60 ))



    while datetime.now() <= current_hour + timedelta(minutes = 60):
        try:
            if aio.receive(pumpstatus.key).value == 'RUNNING': break
            #print('\rmL/min {:10d} -  state {:1d} '.format(round(flow_avg2,2), GPIO.input(inpt)), end = '')
        except KeyboardInterrupt:
            print('exited')
            GPIO.cleanup()
            sys.exit()



GPIO.cleanup()
sys.exit()
