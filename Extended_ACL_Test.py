from netmiko import ConnectHandler
from getpass import getpass
import re
def convert(s): 
  
    # initialization of string to "" 
    str1 = "" 
  
    # using join function join the list s by  
    # separating words by str1 
    return(str1.join(s))
new_acl_file = "Test-20190612-1030.txt"
text2 = open(new_acl_file).readlines()

ydh_pw = getpass("Enter SNS5000 password: ")
ydh = {'device_type': 'cisco_ios', 'ip': '192.168.6.177', 'username': 'sns5000', 'password': ydh_pw, 'secret': ydh_pw, 'port': 22,}
remote_conn = ConnectHandler(**ydh)
switchprompt = remote_conn.find_prompt()[:-1]
remote_conn.enable()
rem_pw = getpass("Enter snsremote password: ")
rem = {'device_type': 'cisco_ios', 'ip': '172.29.0.156', 'username': 'snsremote', 'password': rem_pw, 'secret': rem_pw, 'port': 22,}
remote_conn_rem = ConnectHandler(**rem)
remote_conn_rem.enable()
output = remote_conn.send_command_expect("show access-list 150")
output_run = remote_conn.send_command_expect("show run | inc access-list 150")
output_rem = remote_conn_rem.send_command_expect("show access-list 150")
output_run_rem = remote_conn_rem.send_command_expect("show run | inc access-list 150")
output_list = output.splitlines()
output_run_list = output_run.splitlines()
del output_list[0]
output_rem_list = output_rem.splitlines()
output_run_rem_list = output_run_rem.splitlines()
del output_rem_list[0]
output_array = []
for row in output_list:
    tmp = row.lstrip()
    tmp = tmp.split(" ",1)
    tmp[0] = int(tmp[0])
    output_array.append(tmp)
i=10
output_run_array = []
for row in output_run_list:
    tmp = row.replace("access-list 150 ", "")
    tmp = tmp.replace("   "," ")
    tmp = tmp.replace("  "," ")
    tmp2 = [i, tmp]
    output_run_array.append(tmp2)
    i+=10
output_rem_array = []
for row in output_rem_list:
    tmp = row.lstrip()
    tmp = tmp.split(" ",1)
    tmp[0] = int(tmp[0])
    output_rem_array.append(tmp)
i=10
output_run_rem_array = []
for row in output_run_rem_list:
    tmp = row.replace("access-list 150 ", "")
    tmp = tmp.replace("   "," ")
    tmp = tmp.replace("  "," ")
    tmp2 = [i, tmp]
    output_run_rem_array.append(tmp2)
    i+=10
i=0
for row in text2:
    text2[i] = row.rstrip()
    i+=1
if (len(output_array)>len(text2)):
    print ("iterating output_array")
    for num, entry in enumerate(output_array, start=0):
        if (num>len(text2)-1):
            print ("Line: {} Old: {} || New: NULL".format(num,entry[1]))
        else:
            if (entry[1]==text2[num]):
                print ("Line: {} | Entries match".format(num))
            else:
                print ("Line: {} Old: {} || New: {}".format(num,entry[1],text2[num]))
else:
    print ("iterating text2")
    for num, entry in enumerate(text2, start=0):
        if (num>len(output_array)-1):
            print ("Line: {} Old: NULL || New: {}".format(num,entry))
        else:
            if (output_array[num][1]==entry):
                print ("Line: {} | Entries match".format(num))
            else:
                print ("Line: {} Old: {} || New: {}".format(num,output_array[num][1],entry))

if (len(output_array)>len(text2)):
    print ("Debug info: iterating output_array")
    for num, entry in enumerate(output_array, start=0):
        if (num>len(text2)-1):
            print ("Line: {} Old: {} || New: NULL".format(num,entry[1]))
        else:
            if (entry[1]==text2[num]):
                print ("Line: {} | Entries match".format(num))
            else:
                print ("Line: {} Old: {} || New: {}".format(num,entry[1],text2[num]))
else:
    print ("Debug info: iterating text2")
    max_acl = output_array[len(output_array)-9][0]
    new_offset = 0
    for num, entry in enumerate(text2, start=0):
        if (num>len(output_array)-1-new_offset):
            print ("Line: {} Old: NULL || New: {}".format(num,entry))
        else:
            if (output_array[num+new_offset][1]==entry):
                print ("Line: {} | Entries match".format(num))
            else:
                if (output_array[num+new_offset][0]>max_acl):
                    print ("ACL entry over max. Current: {} Max: {}".format(output_array[num-new_offset][0],max_acl))
                    print ("Line: {} Old: {} || New: {}".format(num,output_array[num-new_offset][1],entry))
                else:
                    if (output_array[num-new_offset+1][1]==entry):
                        new_offset += 1
                        print ("Line: {} | Entries match with offset {}".format(num, new_offset))
                        print ("Line: {} Drop Rule {} {}".format(num,output_array[num][0],output_array[num][1]))
                    else:
                        print ("Line: {} Old: {} || New: {}".format(num,output_array[num-new_offset][1],entry))
