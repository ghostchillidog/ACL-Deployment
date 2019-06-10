from getpass import getpass
import csv
## Prompt for York password
ydh_pw = getpass("Enter SNS5000 password: ")
## Prompt for Scarborough password
sch_pw = getpass("Enter SNS1066 password: ")
## Prepart CSV for import
file="ACL_Update.csv"
## Open CSV file
data=open(file)
## Open input file as a CSV item
datainput=csv.reader(data, delimiter=',')
## Skip first (header) line
headers = next(datainput, None)
## print headers for debug
## print (headers)
device_acl = []
device_list = []
device_location = []
i = 0
for row in datainput:
	## Print row for debug
	## print (row)
	ip = row[0]
	## No entry in CSV for site yet - default to York
	if row[5] == 'YDH':
		ydh = {'device_type': 'cisco_ios', 'ip': ip, 'username': 'sns5000', 'password': ydh_pw, 'secret': ydh_pw, 'port': 22,}
		device_acl.append(row[2])
		device_list.append(ydh)
		device_location.append("YDH")
	elif row[5] == 'SCH':
		sch = {'device_type': 'cisco_ios', 'ip': ip, 'username': 'sns1066', 'password': sch_pw, 'secret': sch_pw, 'port': 22,}
		device_acl.append(row[2])
		device_list.append(sch)
		device_location.append("SCH")
	else:
		print ("Error in device. No site label.")
	i += 1
data.close()
