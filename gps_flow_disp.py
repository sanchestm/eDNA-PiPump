import time
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import serial
import pynmea2
import time, sys
import RPi.GPIO as GPIO
import time, sys
from datetime import datetime, timedelta

inpt = 25
#GPIO.setmode(GPIO.BOARD)



#print('pass import')
################# Display ##############################
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
# Clear display.
disp.fill(0)
disp.show()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
font = ImageFont.load_default()
cmd = "hostname -I | cut -d\' \' -f1"
IP = subprocess.check_output(cmd, shell=True).decode("utf-8")

#print('pass Display IP: '+IP )


#################### GPS ####################################

port = "/dev/ttyACM0"

def parseGPS(val):
    if val.find('GGA') > 0:
        msg = pynmea2.parse(val)
        #print ("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s -- Satellites: %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units,msg.num_sats))
        return  'Lat: '+msg.latitude +'Lon: ' +msg.longitude
    return 0
try:
    serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
except:
    pass

#print('pass GPS')

#################### flowmeter ###############################
GPIO.setup(inpt, GPIO.IN)
GPIO.setup(inpt, GPIO.IN, pull_up_down = GPIO.PUD_UP) #PUD_UP


constant = 1380

global count
count = 0
global long_term_count
long_term_count = 0
delta = 1
#pwmPin = 12
#GPIO.setup(pwmPin, GPIO.OUT)
#pwm = GPIO.PWM(pwmPin, 7)
#GPIO.cleanup(pwmPin)
#GPIO.setwarnings(False)

def countPulse(channel):
   global count
   global long_term_count
   count += 1
   long_term_count += 1

GPIO.add_event_detect(inpt, GPIO.FALLING, callback=countPulse) #GPIO.FALLING



file = open('/home/pi/Desktop/Log.txt', 'a+')

#print('got to loop')
while 1:
    ####################### waiting for change #########################
    long_term_count = 0
    flow_avg = 0
    try:
        gps_location =parseGPS(serialPort.readline().decode("utf-8"), 0)
        #print('found gps')
    except:
        gps_location = 'Not fixed'
    print('about to write to display')
    while long_term_count == 0:
        try:
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            cmd = "hostname -I | cut -d\' \' -f1"
            IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
            CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
            MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
            Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
            draw.text((0, top+0), "IP: "+IP, font=font, fill=255)
            draw.text((0, top+8), CPU, font=font, fill=255)
            draw.text((0, top+16), MemUsage, font=font, fill=255)
            draw.text((0, top+25), gps_location, font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(.1)
        except KeyboardInterrupt:
            print('exited')
            #GPIO.cleanup(pwmPin)
            GPIO.cleanup()
            sys.exit()
    ################## running for 3 min ###############################
    try:
        gps_location =parseGPS(serialPort.readline().decode("utf-8"), 0)
        #print('found gps')
    except:
        gps_location = 'Not fixed'
    min10_delta = time.time() + 60*3
    #print('Started Time         ', '\t', time.asctime(time.localtime()))
    while time.time() <= min10_delta:
        ### reset timer
        future = time.time() + delta
        rate_count = 0
        count = 0
        ### loop to count flowmeter frequency
        while time.time() <= future:
            try:
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                draw.text((0, top+0), "IP: "+IP, font=font, fill=255)
                draw.text((0, top+8), 'Flow(mL/min): ' + str(flow_avg), font=font, fill=255)
                draw.text((0, top+16), 'Liters(L):   ' + str(long_term_count/constant), font=font, fill=255)
                draw.text((0, top+25), 'Cycles: ' + str(long_term_count) , font=font, fill=255)
                disp.image(image)
                disp.show()
                time.sleep(.1)
            except :
                #print('exited')
                GPIO.cleanup()
                time.sleep(.25)
                sys.exit()
        flow_avg = (count/delta)/constant*1000*60
    #print('Stopped Time         ', '\t', time.asctime(time.localtime()))
    #print('Total Flow:          ' + str(long_term_count/constant))
    #print('Cycle number         ' + str(long_term_count))
    file.write('Time {} - flow(L) {:4f}\n'.format( time.asctime(time.localtime()), long_term_count/constant/60 ))
    flow_avg = 0
