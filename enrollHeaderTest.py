#!/usr/bin/python
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
from threading import Timer
import picamera
import os
import shutil #for python copy files
import httplib #FOR PING GOOGLE TO CHECK INTERNET CONNECTIVITY.
import smbus#for i2c device like arduino

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
fontB = ImageFont.truetype('/home/pi/RAW/TestFiles/PIXEARG_.TTF',22 )
font = ImageFont.truetype('/home/pi/RAW/TestFiles/m12.TTF',18 )
fontS=ImageFont.truetype('/home/pi/RAW/TestFiles/runescape_uf.ttf',18 )

padding = -1
top = padding
bottom = height-padding
camera=picamera.PiCamera()
camera.resolution = (320, 240)
S_data = ""
amount_expected=6
amount_received=0
global command_recived
network_status = True
global sock
socket_status=1
server_address = ('192.168.2.215', 12345)
#server_address = ('182.72.165.85', 9010)
#server_address = ('192.168.2.215',1234)
#server_address = ('182.72.165.85',1234)
bus = smbus.SMBus(1) #arduino device 
controller_address = 0x11

#data_to_server=[]
#camera.start_preview()
#time.sleep(2)
#camera.stop_preview()

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

###########################################################################################################
###########################################################################################################
GPIO.setmode(GPIO.BCM)
panic_pin=17
bio_pin=18
GPIO.setup(panic_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(bio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

def check_io_pins(channel):#This function will be qutomatically called if the panic or bio buttons are pressed
	global panic_pin
	global data_to_server
	#print channel
	print "Check io fntn called"
	if GPIO.input(panic_pin)==False and GPIO.input(bio_pin)==True:
		data_to_server.append("Panic")
	elif GPIO.input(bio_pin)==False and GPIO.input(panic_pin)==True:
		data_to_server.append("Bio")
		identify_finger()
	elif GPIO.input(panic_pin)==False and GPIO.input(bio_pin)==False:
		print "shutwown sequence started"
		for i in range(8):
			if GPIO.input(panic_pin)==False and GPIO.input(bio_pin)==False:
				time.sleep(1)
				if i==7:
					draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
					draw.text((0, 30),"Force Shutdown...",  font=fontS, fill=255)
					disp.image(image)
					disp.display()
					data_to_server.append("Force Shutdown")
					time.sleep(1)
					os.system('sudo init 0')		
			else:
				break
	
GPIO.add_event_detect(panic_pin, GPIO.FALLING, callback=check_io_pins, bouncetime=3000)
GPIO.add_event_detect(bio_pin, GPIO.FALLING, callback=check_io_pins,bouncetime=3000)
#############################################################################################################
##############################################################################################################

def commands_to_variable():
	#fileW=open("commands.txt","w")
	#print 'cpmmand to variabl efntn started'
	global command_recived
	global socket_status
	global network_status
	try:
		while(True):
			if(network_status==True):
				if command_recived=='':
					socktdata=sock.recv(6)
					command_recived=socktdata
					time.sleep(0.2)
	except:
		while(socket_status!=None):
			time.sleep(0.1)
		commands_to_variable()
		time.sleep(0.2)
		
		#print command_recived;
		

def reconnect_server():
	print "Reconnected server fntn started"
	#global network_status
	global sock
	global socket_status
	#check_network()
	if network_status==True:
		socket_status=1
		while (socket_status!= None):
			print("Inside reconnect while loop")
			try:
				sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				socket_status=sock.connect(server_address)
				print("Success connecting to server ")
				time.sleep(0.2)
            
			except socket.error as e:
				print(e)
				time.sleep(1)
				reconnect_server()
			
			
			# a=sock.connect(server_address)
			# data_to_server.append("DEVICE ReConnected...")
			#time.sleep(0.1)
			
			
def check_network():
	while(True):
		print "NW status fntn enterd"
		global network_status
		conn = httplib.HTTPConnection("www.google.com",timeout=1)
		try:
			conn.request("HEAD", "/")
			conn.close()
			network_status=True
			print("nw available")
		except:
			conn.close()
			network_status=False
			print ("NW not available")
		finally:
			time.sleep(120)

		
		
def printByteArray(arr):
    return map(hex, list(arr))

def readI2cBus():#read i2c values from controlelr
	#number = bus.read_byte_data(address)
	a=0
	string = ''
	try:
		rep =bus.read_i2c_block_data(controller_address,0)
	except:
		a=1
	if a==0:
		for i in range(0,25):
			if rep[i]!=255:
				string += chr(rep[i])
	print string
	return string

		
def EnrollId(ID):
	global data_to_server
	data_to_server.append("$ACKE#")
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
		data_to_server.append("EOK")
		a=1
		draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
		draw.text((0, 0),"Enrolling ",  font=font, fill=255)
		draw.text((0, 35),"Place Finger ",  font=fontS, fill=255)
		disp.image(image)
		disp.display() 
		f.CmosLed(1)
		while a:	
			data=f.IsPressFinger()
			a=data[0]["Parameter"]
		if a==0: 
			time.sleep(.005)
			f.CaptureFinger()
			data=f.Enroll1()
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
			#f.CmosLed(0)
			
			a=data[0]["Parameter"]
			if a==0:
				a=1
				#f.CmosLed(1)
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
					data=f.Enroll2()
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
					#f.CmosLed(0)
					
					a=data[0]["Parameter"]
					if a==0:
						a=1
						#f.CmosLed(1)
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
							data=f.Enroll3()
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
							
							a=data[0]["Parameter"]
							b=data[0]["ACK"]
							f.CmosLed(0)
							if (b == False and a<200):
								#sock.sendall("DID:%s" % a)
								data_to_server.append("DID:%s" % a)
								print "Duplicate ID of:"
								print a
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 30),"Alredy Enrolled in: ",  font=fontS, fill=255)
								draw.text((0, 45),str(a),  font=fontS, fill=255)
								disp.image(image)
								disp.display()
							elif a==0:
								data_to_server.append("E%sOK" % ID)
								#sock.sendall()
								print "Enroll Success"
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 25),"Enroll Success ",  font=fontS, fill=255)
								disp.image(image)
								disp.display()
							else:
								print "Capture 3rd finger failed"
								data_to_server.append("Capture 3rd image failed")
								draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
								draw.text((0, 0),"Enrolling ",  font=font, fill=255)
								draw.text((0, 35),"Enroll Failed ",  font=fontS, fill=255)
								disp.image(image)
								disp.display()
								f.CmosLed(0)
			
					else:
						print "Capture second finger failed"
						data_to_server.append("Capture 2nd image failed")
						draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
						draw.text((0, 0),"Enrolling ",  font=font, fill=255)
						draw.text((0, 35),"Enroll Failed ",  font=fontS, fill=255)
						disp.image(image)
						disp.display()
						f.CmosLed(0)
			
			else:
				print "Capture 1st finger failed"
				data_to_server.append("Capture 1st image failed")
				draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
				draw.text((0, 0),"Enrolling ",  font=font, fill=255)
				draw.text((0, 35),"Enroll Failed ",  font=fontS, fill=255)
				disp.image(image)
				disp.display()
				f.CmosLed(0)
	
	else:
		print "Id not valid or used"
		data_to_server.append("Used/Invalid ID:%s"%ID)
def DeleteId(id):
	global data_to_server
	data=f.DeleteId(id)
	a=data[0]["Parameter"]
	if a==0:
		data_to_server.append("Delete OK ID:"+str(id))
		print "Deleted ID Success"
	else:
		data_to_server.append("Not Used/Invalid ID:"+str(id))
		print "ID not used"
	
								
def identify_finger():
	global data_to_server
	print"identify fntn called"
	now=time.time()
	f.CmosLed(1)
	a=1
	while (a!=0 and ((time.time()-now)<10)): 
		data=f.IsPressFinger()
		a=data[0]["Parameter"]
	if a==0:
		time.sleep(.01)
		f.CaptureFinger()
		data= f.Identify()
		if data[0]["ACK"]==True and  0<= data[0]["Parameter"] <= 199:
			data_to_server.append("ID:"+str(data[0]["Parameter"]))
			print "id verified"
		elif data[0]["ACK"]==False:
			data_to_server.append("Unknown Finger")
	else:
		data_to_server.append("No finger on sensor")
		
	
	f.CmosLed(0)
def delete_all():
	global data_to_server
	data=f.DeleteAll()
	a=data[0]["ACK"]
	if a==True:
		print "Deleted all"
		data_to_server.append("DLTAOK")
	else:
		print "DB is empty"
		data_to_server.append("Error: DB already Empty")
							
def Get_temp(id):
	global data_to_server
	data=f.CheckEnrolled(id)
	print data
	a=data[0]["Parameter"]
	if a==0:
		template=f.GetTemplate(id)
		temp_data=template[1]['Data']
		data_to_server.append(temp_data)
		#return temp_data
	else:
		print id
		print ":Not Used/Not valid "
		text="Not Used/Invalid ID:"
		text+=str(id)
		data_to_server.append(text)
def Set_temp(id):
	global data_to_server
	print id
	data=f.CheckEnrolled(id)
	print data
	a=data[0]["Parameter"]
	
	if a!=0:
		print "waiting for template"
		data_to_server.append("Waiting For template...")
		template=sock.recv(996)
		print template
		template=bytearray.fromhex(template)
		#print "template in hex"
		#print template
		template= str(template)
		#print "template to string"
		#print template
		data=f.SetTemplate(id,template)
		a=data[1]["Parameter"]
		b=data[1]["ACK"]
		if (b==True and a==0):
			data_to_server.append("Upload Ok ID:"+str(id))
		elif (b==False and (0<=a<=199)):
			data_to_server.append("DID of:"+str(a))
		else:
			data_to_server.append("Template Error")
		#data_to_server.append(data)
		
		print "set template response below"
		print data
	else:
		print id
		print ":Used/Not valid "
		text="Used/Invalid ID:"
		text+=str(id)
		data_to_server.append(text)
	
def audio_capture():
	print "recording audio"
	os.system('arecord -d 5 --device=hw:1,0 --format S16_LE --rate 44100 -c1 audio.wav')
	os.system('lame audio.wav recorded_audio.mp3')
	f = open('recorded_audio.mp3', 'rh')
	print "sending audio"
	l = f.read(1024)
	data_to_server.append(l)
	while (l):
		data_to_server.append(l)
		l = f.read(1024)
		print "sending" 
		time.sleep(0.02)
		#time.sleep(0.01)
	print "Done Sending"
	time.sleep(0.1)
	

	
def cam_capture():
	#print "cam command received"
	camera.capture('test.jpg',quality=10)
	os.system('pkill picamera')
	f = open('test.jpg', 'rh')
	print 'Sending...'
	l = f.read(1024)
	data_to_server.append(l)
	while (l):
		data_to_server.append(l)
		l = f.read(1024)
		print "sending" 
		time.sleep(0.02)
		#time.sleep(0.01)
	print "Done Sending"
	time.sleep(0.1)


	
def send_information():
	print "send into fntn started"
	global data_to_server
	global network_status
	try:
		print "inside try"
		while(True):
			if network_status==True:
				if (len(data_to_server)!=0):
					sock.sendall(data_to_server[0])
					del data_to_server[0]
			time.sleep(0.02)
	except socket.error as e:
		sock.close()
		print "server disconnected"
		data_to_server.append("Server Disconnected")
		reconnect_server()
		send_information()
	
def update_firmware():
	global data_to_server
	data_to_server.append("Updating Firmware...")
	pgm_file='/home/pi/RAW/TestFiles/enrollHeaderTest.py'
	os.system("sudo rm -rf /home/pi/RAW/TestFiles/Box")
	os.system("git clone https://github.com/dinud143/Box.git")
	data_to_server.append("Download Compleated...")
	print"git download complete"
	os.remove(pgm_file)
	shutil.copy( firm_dir,"/home/pi/RAW/TestFiles")
	print "copy and replace complete"
	data_to_server.append("Firmware replaced.")
	
	
def Process_Commands(S_data):
	global data_to_server
	#S_data = sock.recv(6)
	if S_data != "":
		print S_data
		if S_data[0]=='$' and S_data[5]=='#':
			if S_data[1]=='E':
				num=S_data[2:5]
				EnrollId(int(num))
				S_data=""
			elif S_data[1:5]=='JPEG':
				cam_capture()
				S_data=""	
			elif S_data[1:5]=='AUDI':
				thread_send_audio.start()
				S_data=""
			elif S_data[1]=='G':
				num=S_data[2:5]
				Get_temp(int(num))
				S_data=""
			elif S_data[1]=='S':
				num=S_data[2:5]
				Set_temp(int(num))
				S_data=""
			elif S_data =='$DLTA#':
				delete_all()
				S_data=""
			elif S_data[1]=='D':
				num=S_data[2:5]
				DeleteId(int(num))
				S_data=""
			
			elif S_data =='$UPDT#':
				update_firmware()
				S_data=""
			else:
				data_to_server.append("Wrong Input")
				S_data=0
			
		else:
			data_to_server.append("Wrong Input")
			S_data=0
		
	
def show_home_screen():
	draw.rectangle((0,0,width,height), outline=0, fill=0)#clear display
	draw.text((0, 0),"Muthoot",  font=font, fill=255)
	draw.text((10, 30),"ERT",  font=font, fill=255)
	disp.image(image)
	disp.display()
	
f = fp.FingerPi()
data_to_server=[]
print 'Opening connection...'
f.Open(extra_info = True, check_baudrate = True)
print 'Changing baudrate...'
f.ChangeBaudrate(115200)
draw.text((x, 0),"Testing ",  font=font, fill=255)
disp.image(image)
disp.display() 
time.sleep(.1)
command_recived=''
firm_dir = ("/home/pi/RAW/TestFiles/Box/enrollHeaderTest.py")


thread_chk_network=Thread(target=check_network)
thread_chk_network.start()



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ('182.72.165.85', 9010)
thread_reconnect_server=Thread(target=reconnect_server)
thread_reconnect_server.start()







thread_process_recived_data=Thread(target=commands_to_variable)#thread for process rx data
thread_process_recived_data.start()

thread_send_data=Thread(target=send_information)#thread for  tx data
thread_send_data.start()


thread_send_audio=Thread(target= audio_capture)#thread for  audio data
#thread_send_audio.start()




#data_to_server.append("Device COnnected...")
#file=open("commands.txt","r+") 
while(True):
	#print command_recived
	if (command_recived != ''):
		print  "executed before process cmd"
		#print command_recived
		Process_Commands(command_recived)
		command_recived=""
	
		
	
	print network_status
	
	show_home_screen()
	adc=readI2cBus()
	time.sleep(0.2)
	#check_io_pins()
	# try: 
		# print data_to_server[0]
	# except:
		# print "no data"
	# #print data_to_server[1]
	


