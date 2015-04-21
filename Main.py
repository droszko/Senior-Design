#!/usr/bin/env python
#!/usr/bin/python

import datetime
import time
import RPi.GPIO as GPIO
import urllib2
import xml.etree.ElementTree as ET

# The following are global variables which are set to values that 
# are unrealistic for weather data. This allows the program to see if
# something is not correctly being stored.
first_run = "Yes"
future = "NU"
internet = "Active"
temp_f = "NU" #w
weather = "unknown"
wind_mph = "NU" #w
zipcode = "NU"	
wconditions = ["Drizzle", "Light Drizzle", "Heavy Drizzle", "Drizzle"]

#Lists are in this order: Today, Tomorrow, Day After Tomorrow, Another Day After
amt_rain = ["NU","NU","NU","NU"] 
amt_snow = ["NU","NU","NU","NU"] #w
conditions = ["NA", "NA", "NA", "NA"] #w
rain_pct = ["NU","NU","NU","NU"] #w

def main():
#	The getdata function is called in order to update certain global 
#   variables.
	getdata()
	
#	The following lines of code are used to configure the GPIO settings. 	
#	GPIO.setwarnings(False)
#	GPIO.setmode(GPIO.BOARD)
#	GPIO.setup(5, GPIO.OUT)
#	GPIO.setup(7, GPIO.OUT)
	
#	The if statement is used to see if this is the first time that the 
#	code has ran. If so, it will enable the green LED and make sure the
#	red LED is disabled.
	if (first_run == "Yes"):
#		GPIO.output(5, GPIO.LOW)
#		GPIO.output(7, GPIO.LOW)
		print "buffer"
		
	wunderground()
	
# 	Starting parameter check now
	try:
		float(temp_f)
	except:
#		GPIO.output(5, GPIO.HIGH)
#		GPIO.output(7, GPIO.HIGH)
		print "Floatation Device Error 1"
	
	try:
		float(wind_mph)
	except:
#		GPIO.output(5, GPIO.HIGH)
#		GPIO.output(7, GPIO.HIGH)
		print "Floatation Device Error 2"

	try:
		int(future)
	except:
#		GPIO.output(5, GPIO.HIGH)
#		GPIO.output(7, GPIO.HIGH)
		print "Floatation Device Error 3"
	
	if(float(temp_f) <= 32.0):
		print "temp too low"
		return
		
	if(float(wind_mph) >= 20.0):
		print "wind too high"
		return
	
	x = 0
	y = int(future)
	while(x <= y):
		if(float(amt_rain[x]) >= 0.25):
			y = 4
			break
		if(float(amt_snow[x]) >= 0.10):
			y = 4
			break
		if(float(rain_pct[x]) >= 70):
			y = 4
			break
		x = x + 1
		
#	d = datetime.datetime.now()
#	print d.hour

	return
	
def getdata():
	xmlfile_tree = ET.parse("Data.xml")
	xmlfile_root = xmlfile_tree.getroot()
	
	global first_run, future, zipcode
	first_run = xmlfile_root.find("./firstrun").text
	future = xmlfile_root.find("./future").text
	zipcode = xmlfile_root.find("./zipcode").text
	
	xmlfile_tree = ET.ElementTree(xmlfile_root)
	xmlfile_tree.write("Data.xml")	
	return
	
#	The following function called wunderground will be used by the 
#	program to obtain weather data from the wunderground api. The
#	string that is passed into this function will be the zipcode that
#	is provided by the user.
def wunderground():

	if(zipcode == "NU"):
#		GPIO.output(5, GPIO.LOW)
#		GPIO.output(7, GPIO.HIGH)
		print "buffer"

#	The zipcode stored as a global variable is added into the url in order to request the correct weather data.
	url_wunderground = 'http://api.wunderground.com/api/472b20b3716e0a0b/conditions/forecast/q/%s.xml' %zipcode
	
#	In the following code, the program will attempt to pull the xml data
#	from the wunderground api. If it can't it will throw out an error.
	global internet
 	try:
		conditions_file = urllib2.urlopen(url_wunderground)
	except urllib2.HTTPError, e:
#		GPIO.output(5, GPIO.LOW)
#		GPIO.output(7, GPIO.HIGH)
		internet = "Inactive"
		return
	except urllib2.URLError, e:
#		GPIO.output(5, GPIO.LOW)
#		GPIO.output(7, GPIO.HIGH)
		internet = "Inactive"
		return
 	
# 	GPIO.output(5, GPIO.HIGH)
# 	GPIO.output(7, GPIO.LOW)
 	
 	conditions_data = conditions_file.read()	
 	conditions_file.close()
 	conditions_root = ET.fromstring(conditions_data)
 	
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
	
	variable = "w"
	savedata(variable)
	
	return
	
def savedata(variable):
	xmlfile_tree = ET.parse("Data.xml")
	xmlfile_root = xmlfile_tree.getroot()
	
	if(variable == "u"):
		print "u"
		
	elif(variable == "w"):		
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
			
	else:
		return
		
	print datetime.datetime.now()

	
	for frun in xmlfile_root.iter("firstrun"):
			frun.text = "No"
			
	xmlfile_tree = ET.ElementTree(xmlfile_root)
	xmlfile_tree.write("Data.xml")	
	
	return

if __name__ == '__main__':
	main()
