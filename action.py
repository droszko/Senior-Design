#!/usr/bin/env python

import cgi
import cgitb
import xml.etree.ElementTree as ET

cgitb.enable()

print "Content-type: text/html\n\n"

form=cgi.FieldStorage()

xmlfile_tree = ET.parse("Data.xml")
xmlfile_root = xmlfile_tree.getroot()

if "days" not in form:
	print "<body>No data was entered for the days checked, not updating xml file.</body>"
	print "<h1> </h1>"
else:
	days=form["days"].value
	x=1
	
	try:
		int(days)
	except:
		print "<body>The input you provided was not a integer value!</body>"
		print "<h1> </h1>"
		x=2
		
	if(x==1):
		if(int(days) >= 4 or int(days) < 1):
			print "<body>The input for the start hour was not between 1 and 3!</body>"
			print "<h1> </h1>"
			x=2
	
	if(x==1):
		print "<body>The value you inputted is valid and the xml file will be updated!</body>"
		print "<h1> </h1>"
		for da in xmlfile_root.iter("future"):
			da.text = days

###############################################################################################

if "starthour" not in form:
	print "<body>No data was entered for the start hour, not updating xml file.</body>"
	print "<h1> </h1>"
else:
	starthour=form["starthour"].value
	x=1
	
	try:
		int(starthour)
	except:
		print "<body>The input you provided was not a integer value!</body>"
		print "<h1> </h1>"
		x=2
		
	if(x==1):
		if(int(starthour) >= 24 or int(starthour) < 0):
			print "<body>The input for the start hour was not between 00 and 23!</body>"
			print "<h1> </h1>"
			x=2
	
	if(x==1):
		print "<body>The value you inputted is valid and the xml file will be updated!</body>"
		print "<h1> </h1>"
		for sh in xmlfile_root.iter("time_start"):
			sh.text = starthour

###############################################################################################

if "endhour" not in form:
	print "<body>No data was entered for the end hour, not updating xml file.</body>"
	print "<h1> </h1>"
else:
	endhour=form["endhour"].value
	x=1
	
	try:
		int(endhour)
	except:
		print "<body>The input you provided was not a integer value!</body>"
		print "<h1> </h1>"
		x=2
		
	if(x==1):
		if(int(endhour) >= 24 or int(endhour) < 0):
			print "<body>The input for the start hour was not between 00 and 23!</body>"
			print "<h1> </h1>"
			x=2
	
	if(x==1):
		print "<body>The value you inputted is valid and the xml file will be updated!</body>"
		print "<h1> </h1>"
		for eh in xmlfile_root.iter("time_stop"):
			eh.text = endhour

###############################################################################################
	
if "runtime" not in form:
	print "<body>The sprinkler run time was not provided, not updating xml file.</body>"
	print "<h1> </h1>"
else:
	runtime=form["runtime"].value
	x=1
	
	try:
		int(runtime)
	except:
		print "<body>The input you provided was not a integer value!</body>"
		print "<h1> </h1>"
		x=2
		
	if(x==1):
		if(int(runtime) >= 600 or int(runtime) < 0):
			print "<body>The input for the run time was not between 0 and 600!</body>"
			print "<h1> </h1>"
			x=2
	
	if(x==1):
		print "<body>The value you inputted is valid and the xml file will be updated!</body>"
		print "<h1> </h1>"
		for rt in xmlfile_root.iter("run_time"):
			rt.text = runtime

###############################################################################################
	
if "solenoids" not in form:
	print "<body>The number of solenoids was not provided, not updating xml file.</body>"
	print "<h1> </h1>"
else:
	solenoids=form["solenoids"].value
	x=1
	
	try:
		int(solenoids)
	except:
		print "<body>The input you provided was not a integer value!</body>"
		print "<h1> </h1>"
		x=2
		
	if(x==1):
		if(int(solenoids) >= 9 or int(solenoids) < 0):
			print "<body>The input for the number of solenoids was not between 0 and 8!</body>"
			print "<h1> </h1>"
			x=2
	
	if(x==1):
		print "<body>The value you inputted is valid and the xml file will be updated!</body>"
		print "<h1> </h1>"
		for sn in xmlfile_root.iter("solenoids"):
			sn.text = solenoids

###############################################################################################	
	
if "zipcode" not in form:
	print "<body>A zipcode was not provided, not updating xml file.</body>"
	print "<h1> </h1>"
else:
	zipcode=form["zipcode"].value
	x=1
	
	if(len(zipcode) != 5):
		print "<body>Warning, the length of the zipcode you inputted was not 5 digits! Updating xml file.</body>"
		print "<h1> </h1>"
		x=2
	
	if(x==1):
		print "<body>The value you inputted is valid and the xml file will be updated!</body>"
		print "<h1> </h1>"

	for zc in xmlfile_root.iter("zipcode"):
		zc.text = zipcode
	
xmlfile_tree = ET.ElementTree(xmlfile_root)
xmlfile_tree.write("Data.xml")
