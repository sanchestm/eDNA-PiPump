import RPi.GPIO as GPIO
import time, sys
GPIO.setmode(GPIO.BOARD)
inpt = 13
GPIO.setup(inpt, GPIO.IN)
rate_count = 0
tot_count = 0
minutes = 0
constant = 38
time_new = 0.0

print('Time         ', '\t', time.asctime(time.localtime()))
while True:
    future = time.time() + 1
    rate_count = 0
    while time.time() <= future:
        if GPIO.input(inpt) != 0:
            rate_count += 1
            tot_count += 1
        try:  pass #print(GPIO.input(inpt), end= '')
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()
    print('\n mL/min    ', round(rate_count/constant, 4) )
    #print('Total liters ', round(tot_count*constant,  4))



print('exited')
GPIO.cleanup()
