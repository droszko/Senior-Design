#!/usr/bin/env python
#!/usr/bin/python

import urllib2
import xml.etree.ElementTree as ET

# The following are global variables which are set to values that 
# are unrealistic for weather data. This allows the program to see if
# something is not correctly being stored.
temp_c = 9999.99
temp_f = 9999.99 
weather = "unknown"
wind_mph = 999
zipcode = 11790	
#Lists are in this order: Today, Tomorrow, Day After Tomorrow, Another Day After
amt_rain = [999,999,999,999]
amt_snow = [999,999,999,999]
conditions = ["NA", "NA", "NA", "NA"]
rain_pct = [999,999,999,999]

def main():
	wunderground()
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
def wunderground():
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
	global temp_f, temp_c, weather, wind_mph
	temp_f = conditions_root.find("./current_observation/temp_f").text
	temp_c = conditions_root.find("./current_observation/temp_c").text	
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
		for temp in xmlfile_root.iter("temp_c"):
			temp.text = temp_c
		for temp in xmlfile_root.iter("temp_f"):
			temp.text = temp_f
		for pop in xmlfile_root.iter("pop"):
			pop.text = rain_pct[0]
			rotate = rain_pct[0]
			rain_pct.pop(0)	
			rain_pct.append(rotate)
		for wind in xmlfile_root.iter("wind_mph"):
			wind.text = wind_mph
		
	else:
		return
	
	xmlfile_tree = ET.ElementTree(xmlfile_root)
	xmlfile_tree.write("Data.xml")
	
	return

if __name__ == '__main__':
	main()
