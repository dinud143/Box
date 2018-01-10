# Copyright (c) 2017 Adafruit Industries
# Author: Dinu D
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import RPi.GPIO as GPIO
import fingerpi as fp
import pickle
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import socket
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from threading import Thread
import picamera
import os


import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_bus=1)
# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
# Initialize library.

disp.begin()
# Clear display.
disp.clear()
disp.display()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
fontB = ImageFont.truetype('PIXEARG_.TTF',22 )
font = ImageFont.truetype('PIXEAB__.TTF',22 )
fontS=ImageFont.truetype('runescape_uf.ttf',18 )
padding = -1
top = padding
bottom = height-padding
camera=picamera.PiCamera()
camera.resolution = (320, 240)
S_data = ""
#camera.start_preview()
#time.sleep(2)
#camera.stop_preview()

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf',18)
#font = ImageFont.truetype('runescape_uf.ttf',22 )

GPIO.setmode(GPIO.BCM)
A_pin=17
GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
###########################################################################

def commands_to_variable():
	#fileW=open("commands.txt","w")
	#print 'cpmmand to variabl efntn started'
	global command_recived
	while(True):
		if command_recived=='':
			socktdata=sock.recv(6)
			command_recived=socktdata
		
		#print command_recived;
		
		
		
	
def printByteArray(arr):
    return map(hex, list(arr))


	
def EnrollId(ID):
	draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
	draw.text((0, 0),"Enrolling ",  font=font, fill=255)
	disp.image(image)
	disp.display() 
	a=1
	print "ID=%s"% ID
	data=f.EnrollStart(ID)
	a=data[0]["Parameter"]
	print a
	if a==0:
		sock.sendall("EOK")
		a=1
		f.CmosLed(1)
		draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
		draw.text((0, 0),"Enrolling ",  font=font, fill=255)
		draw.text((0, 35),"Place Finger ",  font=fontS, fill=255)
		disp.image(image)
		disp.display() 
		while a:	
			data=f.IsPressFinger()
			a=data[0]["Parameter"]
		if a==0: 
			time.sleep(.01)
			f.CaptureFinger()
			finger=f.IsPressFinger()
			finger_d=finger[0]["Parameter"]
			while(finger_d == 0):
				finger=f.IsPressFinger()
				finger_d=finger[0]["Parameter"]
				draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
				draw.text((0, 0),"Enrolling ",  font=font, fill=255)
				draw.text((0, 30),"Remove Finger",  font=fontS, fill=255)
				disp.image(image)
				disp.display()
			f.CmosLed(0)
			data=f.Enroll1()
			a=data[0]["Parameter"]
			if a==0:
				a=1
				f.CmosLed(1)
				draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
				draw.text((0, 0),"Enrolling ",  font=font, fill=255)
				draw.text((0, 30),"Place Same ",  font=fontS, fill=255)
				draw.text((40, 45),"Finger Again",  font=fontS, fill=255)
				disp.image(image)
				disp.display()
				while a: 
					data=f.IsPressFinger()
					a=data[0]["Parameter"]
				if a==0: 
					time.sleep(.01)
					f.CaptureFinger()
					finger=f.IsPressFinger()
					finger_d=finger[0]["Parameter"]
					while(finger_d == 0):
						finger=f.IsPressFinger()
						finger_d=finger[0]["Parameter"]
						draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
						draw.text((0, 0),"Enrolling ",  font=font, fill=255)
						draw.text((0, 30),"Remove Finger",  font=fontS, fill=255)
						disp.image(image)
						disp.display()
					f.CmosLed(0)
					data=f.Enroll2()
					a=data[0]["Parameter"]
					if a==0:
						a=1
						f.CmosLed(1)
						draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
						draw.text((0, 0),"Enrolling ",  font=font, fill=255)
						draw.text((0, 30),"Place Same ",  font=fontS, fill=255)
						draw.text((40, 45),"Finger Again",  font=fontS, fill=255)
						disp.image(image)
						disp.display()
						while a:
							data=f.IsPressFinger()
							a=data[0]["Parameter"]
						if a==0:
							time.sleep(.01)
							f.CaptureFinger()
							finger=f.IsPressFinger()
							finger_d=finger[0]["Parameter"]
							while(finger_d == 0):
								finger=f.IsPressFinger()
								finger_d=finger[0]["Parameter"]
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 30),"Remove Finger",  font=fontS, fill=255)
								disp.image(image)
								disp.display()
							f.CmosLed(0)
							data=f.Enroll3()
							a=data[0]["Parameter"]
							b=data[0]["ACK"]
							if (b == False and a<200):
								sock.sendall("DID:%s" % a)
								print "Duplicate ID of:"
								print a
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 30),"Alredy Enrolled in: ",  font=fontS, fill=255)
								draw.text((0, 45),str(a),  font=fontS, fill=255)
								disp.image(image)
								disp.display()
							elif a==0:
								sock.sendall("E%sOK" % ID)
								print "Enroll Success"
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 25),"Enroll Success ",  font=fontS, fill=255)
								disp.image(image)
								disp.display()
							else:
								print "Capture 3rd finger failed"
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 35),"Enroll Failed ",  font=fontS, fill=255)
								disp.image(image)
								disp.display()
			
					else:
						print "Capture second finger failed"
						draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
						draw.text((0, 0),"Enrolling ",  font=font, fill=255)
						draw.text((0, 35),"Enroll Failed ",  font=fontS, fill=255)
						disp.image(image)
						disp.display()
			
			else:
				print "Capture 1st finger failed"
				draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
				draw.text((0, 0),"Enrolling ",  font=font, fill=255)
				draw.text((0, 35),"Enroll Failed ",  font=fontS, fill=255)
				disp.image(image)
				disp.display()
	
	else:
		print "Id not valid or used"
							

def delete_all():
	data=f.DeleteAll()
	a=data[0]["ACK"]
	if a==True:
		print "Deleted all"
	else:
		print "DB is empty"
							
def Get_temp(id):
	data=f.CheckEnrolled(id)
	print data
	a=data[0]["Parameter"]
	if a==0:
		template=f.GetTemplate(id)
		temp_data=template[1]['Data']	
		return temp_data
	else:
		print id
		print ":Not Used/Not valid "
		text="Not Used/Invalid ID:"
		text+=str(id)
		return text
def Set_temp(id):
	print id
	data=f.CheckEnrolled(id)
	print data
	a=data[0]["Parameter"]
	
	if a!=0:
		print "waiting for template"
		template=sock.recv(996)
		print template
		template=bytearray.fromhex(template)
		#print "template in hex"
		#print template
		template= str(template)
		#print "template to string"
		#print template
		data=f.SetTemplate(id,template)
		print "set template response below"
		print data
	else:
		print id
		print ":Used/Not valid "
		text="Used/Invalid ID:"
		text+=str(id)
		return text	
	
		
	
	
	
	
	
def Process_Commands(S_data):
	#S_data = sock.recv(6)
	if S_data != "":
		print S_data
		if S_data[0]=='$' and S_data[5]=='#':
			if S_data[1]=='E':
				num=S_data[2:5]
				EnrollId(int(num))
				S_data=""
			elif S_data[1:5]=='JPEG':
				print "cam command received"
				camera.capture('test.jpg',quality=10)
				os.system('pkill picamera')
				f = open('test.jpg', 'rh')
				print 'Sending...'
				l = f.read(1024)
				while (l):
					sock.send(l)
					l = f.read(1024)
					print "sending" 
					time.sleep(0.01)
				print "Done Sending"
				#time.sleep(30)
				S_data=""	
			elif S_data[1]=='G':
				num=S_data[2:5]
				sock.sendall(Get_temp(int(num)))
				S_data=""
			elif S_data[1]=='S':
				num=S_data[2:5]
				Set_temp(int(num))
				S_data=""
			elif S_data =='$DLTA#':
				delete_all()
				S_data=""
			
		else:
			sock.sendall("Wrong Input")
			S_data=0
		
	
def show_home_screen():
	draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
	draw.text((0, 0),"Muthoot",  font=font, fill=255)
	draw.text((10, 30),"ERT",  font=font, fill=255)
	disp.image(image)
	disp.display()
	
f = fp.FingerPi()
print 'Opening connection...'
f.Open(extra_info = True, check_baudrate = True)
print 'Changing baudrate...'
f.ChangeBaudrate(115200)
draw.text((x, 0),"Testing ",  font=font, fill=255)
disp.image(image)
disp.display() 
time.sleep(.1)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('182.72.165.85', 9010)
sock.connect(server_address)
sock.sendall("Device Connected....... ")
amount_expected=6
amount_received=0
global command_recived
command_recived=''

t=Thread(target=commands_to_variable)
t.start()
#file=open("commands.txt","r+") 
while(True):
	#print command_recived
	if (command_recived != ''):
		print  "executed before process cmd"
		#print command_recived
		Process_Commands(command_recived)
		command_recived=""
		
	
	#print "printed above"
	#Process_Commands()
	show_home_screen()
	#print 'loop\n'
	#print 'loop exit'
	#EnrollId(int(data))
        
		
							
	

	
	
# if a==1:
	# print 'Enroll1 fail'
# else:
	# a=1
	# while a:
		# f.CmosLed(1) 
		# data=f.IsPressFinger()
		# a=data[0]["Parameter"]
	# f.CaptureFinger()
	# f.CmosLed(0)
	# data=f.Enroll2()
	# a=data[0]["Parameter"]
	# if a==1:
		# print 'Enroll2 fail'
	# else:
		# a=1
		# while a:
			# f.CmosLed(1) 
			# data=f.IsPressFinger()
			# a=data[0]["Parameter"]
		# f.CaptureFinger()
		# f.CmosLed(0)
		# data=f.Enroll2()
		# a=data[0]["Parameter"]
		# if a==1:
			# print 'Enroll3 fail'
		# else:
			# a=1
			# while a:
				# f.CmosLed(1) 
				# data=f.IsPressFinger()
				# a=data[0]["Parameter"]
			# f.CaptureFinger()
			# f.CmosLed(0)
			# data=f.Enroll3()
			# a=data[0]["Parameter"]
		

	





# while True:

    # time.sleep(.01)

    # # Write two lines of text.

    # draw.text((x, 20),       "Testing ",  font=font, fill=255)
    # # Display image.
    # disp.image(image)
    # disp.display() 
    # if GPIO.input(A_pin): # button is released
    	# f.CmosLed(False)
    # else: # button is pressed:
        # f.CmosLed(True)
	# time.sleep(.05)
	# f.CmosLed(False)
	# f.Identify()
