#!/usr/bin/env python
#!/usr/bin/python

import urllib2
import xml.etree.ElementTree as ET
from xml.dom import minidom

# The following are global variables which are set to values that 
# are unrealistic for weather data. This allows the program to see if
# something is not correctly being stored.
temperature_f = 9999.99
temperature_c = 9999.99 
zipcode = 00000	
weather = "nothing"
wind_mph = 999
#Lists are in this order: Today, Tomorrow, Day After Tomorrow, Another Day After
amount_of_rain = [999,999,999,999]
amount_of_snow = [999,999,999,999]
chance_of_rain = [999,999,999,999]
condition_forecast = ["NA", "NA", "NA", "NA"]

def main():
#	zipcode = 11790
	datafile()
#	wunderground(zipcode)
	return 0
	
def datafile():
	xmlfile_tree = ET.parse("Data.xml")
	xmlfile_root = xmlfile_tree.getroot()
	
	mylist = ["123", "345", "567", "789"]
	for value in xmlfile_root.iter("condition"):
		value.text = mylist[0]
		mylist.pop(0)
	
	xmlfile_tree = ET.ElementTree(xmlfile_root)
	xmlfile_tree.write("Data.xml")
	
#	The following function called wunderground will be used by the 
#	program to obtain weather data from the wunderground api. The
#	string that is passed into this function will be the zipcode that
#	is provided by the user.
def wunderground(zipcode):
#	The zipcode passed into this function is now added into our api url.	
	url_wunderground = 'http://api.wunderground.com/api/472b20b3716e0a0b/conditions/forecast/q/%s.xml' %zipcode
	
#	In the following code, the program will attempt to pull the xml data
#	from the wunderground api. If it can't it will throw out an error.
 	try:
		conditions_file = urllib2.urlopen(url_wunderground)
	except urllib2.HTTPError, e:
		print "This program has encountered an HTTPError: "
		print e.code
		return
	except urllib2.URLError, e:
		print "This program has encountered an URLError: "
		print e.args
		return
 	
 	conditions_data = conditions_file.read()	
 	conditions_file.close()
 	conditions_root = ET.fromstring(conditions_data)
 	
 	global amount_of_rain, amount_of_snow, chance_of_rain
	for forecastday in conditions_root.findall("./forecast/simpleforecast/forecastdays/forecastday"):
		amount_of_rain.pop(0)
		amount_of_rain.append(forecastday.find("qpf_allday/in").text)
		amount_of_snow.pop(0)
		amount_of_snow.append(forecastday.find("snow_allday/in").text)
		chance_of_rain.pop(0)
		chance_of_rain.append(forecastday.find("pop").text)
		condition_forecast.pop(0)
		condition_forecast.append(forecastday.find("conditions").text)
	
#	The global keyword is used in order to alter global variables, whose
#	values will be replaced by those from the element tree.
	global temperature_f, temperature_c, weather, wind_mph
	temperature_f = conditions_root.find("./current_observation/temp_f").text
	temperature_c = conditions_root.find("./current_observation/temp_c").text	
	weather = conditions_root.find("./current_observation/weather").text
	wind_mph = conditions_root.find("./current_observation/wind_mph").text

	return
	
if __name__ == '__main__':
	main()

#   Gave back the temperature, FUCK YES!!!!!!! SAVE THIS CODE
#	From my understanding, conditions_root is a list, therefore it 
# 	must be placed into a for loop for stuff to come out right
# 	for temp in conditions_root.findall('current_observation'):
# 		temper = float(temp.find('temp_f').text)
# 		print temper

#	Found this code second, but the main issue was that findall command
#	returned a list, therefore you could not use .find or .text on it
#	temperature_f = conditions_root.find("./current_observation/temp_f").text
