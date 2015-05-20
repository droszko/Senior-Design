#!/usr/bin/env python
#!/usr/bin/python

from datetime import datetime
import time
import RPi.GPIO as GPIO
import urllib2
import xml.etree.ElementTree as ET

#	 The following are global variables which are set to NU, which means
# 	not updated. This is done so that the initial state of these variables
# 	aren't saved from a previous run through, and so that the code could
# 	check if the variables are loaded with correct data.

# 	The following variables are used to:
#	 Determine if this is the first time this program has ran.
first_run = "Yes"	
	
# 	Store the number of flow meter pulses detected during watering.
flow_loops = 0	
		
#	 Store the number of days which the porgram checks the forecast for.
future = "NU"

# 	Store the number of seconds for which the solenoidw will be openned for.
run_time = "NU"

# 	Store the number of solenoids connected to the Pi.
solenoids = "NU"

# 	Store the temperature obtained from online.
temp_f = "NU"

#	 Store the current condition obtained from online.
weather = "unknown" 

# 	Store the current wind speed.
wind_mph = "NU"

#	 Store the zipcode of the user.
zipcode = "NU"	

#	Store a value that shows if there is an active internet connection.
connection = "Active"

# 	Determine if the program should halt accessing a function due to a lack of an internet connection.
halt_var = 1

# 	Store the number of days between the last weather update and today.
diff_days = "NU"

# 	Store the month, day and year of the last update.
month = "NU"
day = "NU"
year="NU"

# 	Store the hours between which the program can begin watering.
lower_time = "NU"
upper_time = "NU"

# 	Lists are in this order: Today, Tomorrow, Day After Tomorrow, Another Day After
#	 Stores the expected amount of rain.
amt_rain = ["NU","NU","NU","NU"]

# 	Stores the expected amount of snow.
amt_snow = ["NU","NU","NU","NU"]

# 	Stores the expected conditions.
conditions = ["NU", "NU", "NU", "NU"]

# 	Stores the chance of rain/snow.
rain_pct = ["NU","NU","NU","NU"]

def main():
#	The getdata function is called in order to update global variables
#   from the stored xml file.
	getdata()
	
#	The following lines of code are used to configure the GPIO settings. 	
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(7, GPIO.OUT)
	GPIO.setup(11, GPIO.OUT)
	
#	Flowmeter
	GPIO.setup(8, GPIO.IN)
	
#	Interrupt Button
	GPIO.setup(15,GPIO.IN)
	
#	Solenoids
	GPIO.setup(24, GPIO.OUT)
	GPIO.setup(26, GPIO.OUT)
	
#	Interrupts / Events
	GPIO.add_event_detect(8, GPIO.FALLING, callback=flowcount)
	GPIO.add_event_detect(15, GPIO.RISING, callback=buttoninterrupt)
	
#	The if statement is used to see if this is the first time that the 
#	code has ran. If so, it will enable the green LED and make sure the
#	red LED is disabled. This will also set the outputs to the relays to
#	low so that they are closed.
	if (first_run == "Yes"):
		GPIO.output(7, GPIO.LOW)
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(24, GPIO.LOW)
		GPIO.output(26, GPIO.LOW)

#	Infinite while loop where the program will check the time every 45
#	seconds, if the time is a factor of 10 minutes, it will begin calling
#	functions.		
	x = 1
	while(x==1):
		if(minute == 00 or minute == 10 or minute == 20 or minute == 30 or minute == 40 or minute == 50):
			# Call the wunderground function to obtain weather data from online api.
			wunderground()
			# Check if halt variable allows for the continuing of this program.
			if(halt_var == 1):
				# If the halt variable is 1, the parameter_check function is called.
				parameter_check()
		
		# Sleep for 45 seconds and check the current time.
		time.sleep(45)
		time_now = datetime.now()
		minute = time_now.minute
		print "Waiting"
		
###### IGNORE
#	The wunderground function is called in order to retrieve weather
#	data from the wunderground api.

#	wunderground()
#	if(halt_var == 1):
#		parameter_check()

	return
	
#	The getdata function found below is used to retrieve data from the stored
#	xml file and places them into global variables.
def getdata():
#	Opening of the xml file and parsing the data into an element tree.
	xmlfile_tree = ET.parse("Data.xml")
	xmlfile_root = xmlfile_tree.getroot()
	
#	Getting certain data from the xml file and placing them into the
#	first_run, future, run_time, solenoids and zipcode global variables.
	global first_run, future, run_time, solenoids, zipcode
	first_run = xmlfile_root.find("./firstrun").text
	future = xmlfile_root.find("./future").text
	run_time = xmlfile_root.find("./run_time").text
	solenoids = xmlfile_root.find("./solenoids").text
	zipcode = xmlfile_root.find("./zipcode").text
	
#	Getting certain data from the xml file and placing them into the day,
#	month and year global variables.
	global day, month, year
	day = xmlfile_root.find("./day").text
	month = xmlfile_root.find("./month").text
	year = xmlfile_root.find("./year").text
	
#	Getting certain data from the xml file and placing them into the
#	lower_time and upper_time global variables.
	global lower_time, upper_time
	lower_time = xmlfile_root.find("./time_start").text
	upper_time = xmlfile_root.find("./time_stop").text
	
#	Getting certain data from the xml file and placing them into the
#	amt_rain, amt_snow and rain_pct global variables.
	global amt_rain, amt_snow, rain_pct
	for amt in xmlfile_root.findall("./forecast/rain"):
		amt_rain.pop(0)
		amt_rain.append(amt.text)

	for amt in xmlfile_root.findall("./forecast/snow"):
		amt_snow.pop(0)
		amt_snow.append(amt.text)
		
	for pct in xmlfile_root.findall("./forecast/pop"):
		rain_pct.pop(0)
		rain_pct.append(amt.text)
		
#	Closing the xml file.
	xmlfile_tree = ET.ElementTree(xmlfile_root)
	xmlfile_tree.write("Data.xml")	
	return
	
#	The following function called wunderground will be used by the 
#	program to obtain weather data from the wunderground api. The
#	string that is passed into this function will be the zipcode that
#	is provided by the user.
def wunderground():
	
#	Resets the global variables connection and halt_var.
	global connection, halt_var
	connection = "Active"
	halt_var = 1
	
#	Check if zipcode is updated by user. If the zipcode is not updated,
#	toggle the LEDs, call the errorhandler function and set the halt_var
# 	variable to zero.
	if(zipcode == "NU"):
		GPIO.output(7, GPIO.HIGH)
		GPIO.output(11, GPIO.LOW)
		errorhandler(zipcode)
		halt_var = 0
		return
		
	global day, month, year
	
	if(day != "NU" and month != "NU" and year != "NU"):
		global diff_days
		lastupdate = datetime.strptime(day +" " +month +" " +year, "%d %m %Y")
		currentdate = datetime.now()
		delta = d1-d0
		diff_days = delta.days

#	The zipcode stored as a global variable is added into the url in order to request the correct weather data.
	url_wunderground = 'http://api.wunderground.com/api/472b20b3716e0a0b/conditions/forecast/q/%s.xml' %zipcode
	
#	In the following code, the program will attempt to pull the xml data
#	from the wunderground api. If it can't it will throw out an error.
 	try:
		conditions_file = urllib2.urlopen(url_wunderground)
	except urllib2.HTTPError, e:
		GPIO.output(7, GPIO.HIGH)
		GPIO.output(11, GPIO.LOW)
		errorhandler("http")
		connection = "Inactive"
		if(diff_days >= 3 or diff_days == "NU"):
			halt_var = 0
		return
	except urllib2.URLError, e:
		GPIO.output(7, GPIO.HIGH)
		GPIO.output(11, GPIO.LOW)
		errorhandler("url")
		connection = "Inactive"
		if(diff_days >= 3 or diff_days == "NU"):
			halt_var = 0
		return
 	
#	Placing the stored xml data into an element tree.
 	conditions_data = conditions_file.read()	
 	conditions_file.close()
 	conditions_root = ET.fromstring(conditions_data)
 
#	Placing weather data into global variables. 
 	global amt_rain, amt_snow, conditions, rain_pct
	for forecastday in conditions_root.findall("./forecast/simpleforecast/forecastdays/forecastday"):
		amt_rain.pop(0)
		amt_rain.append(forecastday.find("qpf_allday/in").text)
		amt_snow.pop(0)
		amt_snow.append(forecastday.find("snow_allday/in").text)
		conditions.pop(0)
		conditions.append(forecastday.find("conditions").text)
		rain_pct.pop(0)
		rain_pct.append(forecastday.find("pop").text)
	
#	The global keyword is used in order to alter global variables, whose
#	values will be replaced by those from the element tree.
	
	global temp_f, weather, wind_mph
	temp_f = conditions_root.find("./current_observation/temp_f").text
	weather = conditions_root.find("./current_observation/weather").text
	wind_mph = conditions_root.find("./current_observation/wind_mph").text
	
	savedata()
	
	return
	
def parameter_check():
	global temp_f, wind_mph, future, lower_time, run_time, solenoids, upper_time
	global amt_rain, amt_snow, rain_pct
	
	try:
		float(temp_f)
		float(wind_mph)
	except:
		GPIO.output(7, GPIO.HIGH)
		GPIO.output(11, GPIO.HIGH)
		errorhandler("floaterror")
	
	try:
		int(future)
		int(lower_time)
		int(run_time)
		int(solenoids)
		int(upper_time)
	except:
		GPIO.output(7, GPIO.HIGH)
		GPIO.output(11, GPIO.HIGH)
		errorhandler("interror")
	
	if(float(temp_f) <= 32.0):
		print "temp too low"
		return
		
	if(float(wind_mph) >= 25.0):
		print "wind too high"
		return
		
	loop_variable = int(future)
		
	if(connection == "Inactive"):
		loop_variable = 3
		
	x = 0
	outlook = "Good"
	while(x <= loop variable):
		if(float(amt_rain[x]) >= 0.25):
			x = future
			outlook = "Bad"
			break
		if(float(amt_snow[x]) >= 0.10):
			x = future 
			outlook = "Bad"
			break
		if(float(rain_pct[x]) >= 70):
			x = future
			outlook = "Bad"
			break
		x = x + 1
		
	if(outlook == "Bad"):
		return
		
	time_now = datetime.now()
	hour = time_now.hour
	
	if(int(lower_time) < int(upper_time)):
		if(hour < int(lower_time) or hour > int(upper_time)):
			return
	elif(int(upper_time) < int(lower_time)):
		if(hour > int(upper_time) and hour < int(lower_time)):
			return
	
	wateringcycle()
	
	return

def savedata(variable):
	xmlfile_tree = ET.parse("Data.xml")
	xmlfile_root = xmlfile_tree.getroot()
	
	for condition in xmlfile_root.iter("condition"):
		condition.text = conditions[0]
		rotate = conditions[0]
		conditions.pop(0)
		conditions.append(rotate)
	for rain in xmlfile_root.iter("rain"):
		rain.text = amt_rain[0]
		rotate = amt_rain[0]
		amt_rain.pop(0)
		amt_rain.append(rotate)
	for snow in xmlfile_root.iter("snow"):
		snow.text = amt_snow[0]
		rotate = amt_snow[0]
		amt_snow.pop(0)	
		amt_snow.append(rotate)
	for temp in xmlfile_root.iter("temp_f"):
		temp.text = temp_f
	for pop in xmlfile_root.iter("pop"):
		pop.text = rain_pct[0]
		rotate = rain_pct[0]
		rain_pct.pop(0)	
		rain_pct.append(rotate)
	for update in xmlfile_root.iter("update"):
		update.text = "1"
	for wind in xmlfile_root.iter("wind_mph"):
		wind.text = wind_mph
		
	date = datetime.now()
	month = str(date.month)
	day = str(date.day)
	year = str(date.year)
	
	for datetimevalue in xmlfile_root.iter("month"):
		datetimevalue.text = month
	for datetimevalue in xmlfile_root.iter("day"):
		datetimevalue.text = day
	for datetimevalue in xmlfile_root.iter("year"):
		datetimevalue.text = year
	
	for frun in xmlfile_root.iter("firstrun"):
			frun.text = "No"
			
	xmlfile_tree = ET.ElementTree(xmlfile_root)
	xmlfile_tree.write("Data.xml")	
	
	return

def wateringcycle():
#	Remove the interrupt for the push button.
	GPIO.remove_event_detect(15)
	
#	Set loop variable to 0
	x = 0
	
#	For loop which will enable and disable each solenoid for a user
#	specified amount of time. At the current moment, the loop is only
#	set up for two solenoids during testing.
	for x in range(0, int(solenoids)):
		#If loop variable is 0, open the first solenoid.
		if(x == 0):
			print "Solenoid 1 is open"
			GPIO.output(24, GPIO.HIGH)
			time.sleep(int(run_time))
			GPIO.output(24, GPIO.LOW)
			print "Solenoid 1 is closed"
			time.sleep(3)
		#If loop variable is 1, open the second solenoid
		elif(x == 1):
			print "Solenoid 2 is open"
			GPIO.output(26, GPIO.HIGH)
			time.sleep(int(run_time))
			GPIO.output(26, GPIO.LOW)
			print "Solenoid 2 is closed"
			time.sleep(3)
		x=x+1
		
#	Determining the amount of liters used by the watering cycle.	
	global flow_loops
	flow_rate = 0.0
	mins = (int(run_time)*2) / 60.0
	flow_rate = flow_loops / (7.5*mins)
	
	flow_loops = 0
	
	f = open("WaterUsage.txt", 'a')
	d = datetime.now()
	
	f.write('\n')
	f.write(str(d) +": " + flow_rate +" Liters of water were used.")
	
	f.close()
	
#	Adding the inteerupt for the push button back.
	GPIO.add_event_detect(15, GPIO.RISING, callback=buttoninterrupt)
	return
	
def flowcount(channel):
	global flow_loops
	flow_loops += 1
	return
	
def buttoninterrupt():
	global run_time
	storagevariable = run_time
	run_time = 15
	
	wateringcycle()
	
	run_time = storagevariable
	return
	
def errorhandler(error_code):
	f = open("ErrorLog.txt", 'a')
	d = datetime.now()
	
	if(error_code == "floaterror"):
		f.write('\n')
		f.write(str(d) +": " +"An issue arose when attempting to convert a string into a float variable")
	elif(error_code == "http"):
		f.write('\n')
		f.write(str(d) +": " +"A HTTP error has occured during the weather underground api request")
	elif(error_code == "interror"):
		f.write('\n')
		f.write(str(d) +": " +"An issue arose when attempting to convert a string into a integer variable")
	elif(error_code == "url"):
		f.write('\n')
		f.write(str(d) +": " +"An URL error has occured during the weather underground api request")
	elif(error_code == "zipcode"):
		f.write('\n')
		f.write(str(d) +": " +"Zipcode is not updated on the program")
	
	f.close()
	return
if __name__ == '__main__':
	main()
