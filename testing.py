from netmiko import ConnectHandler
from getpass import getpass
def index_2d(data, search):
    for i, e in enumerate(data):
        try:
            return i, e.index(search)
        except ValueError:
            pass
    raise ValueError("{} is not in list".format(repr(search)))

end_acl_file = "Test-20190612-1030.txt"
end_acl = open(end_acl_file).readlines()
ydh_pw = getpass("Enter SNS5000 password: ")
rem_pw = getpass("Enter snsremote password: ")
ydh = {'device_type': 'cisco_ios', 'ip': '192.168.6.177', 'username': 'sns5000', 'password': ydh_pw, 'secret': ydh_pw, 'port': 22,}
rem = {'device_type': 'cisco_ios', 'ip': '172.29.0.156', 'username': 'snsremote', 'password': rem_pw, 'secret': rem_pw, 'port': 22,}
remote_conn = ConnectHandler(**ydh)
remote_conn.enable()
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
for row in end_acl:
    end_acl[i] = row.rstrip()
    i+=1

running_acl = output_rem_array
i = 0
acl_update = []
rule_match = False
rule_match_end = False
rule_match_run = False
while i < len(end_acl)-1:
    if (end_acl[i] == running_acl[i][1]):
        print ("Line | {:3d} | Matching rule: {}".format(i,end_acl[i]))
        i+=1
    else:
        print ("Line | {:3d} | end_acl: {} || running_acl: {}".format(i,end_acl[i],running_acl[i][1]))
        try:
            rule_match_run = index_2d(running_acl,end_acl[i])
        except:
            print ("!EXCEPTION - Line {} | Running Config".format(i))
        try:
            rule_match_end = end_acl.index(running_acl[i][1])
        except:
            print ("!EXCEPTION - Line {} | End Config".format(i))
        print ("Line | {:3d} | End Location: {}  ||  Run Location {}".format(i,rule_match_end,rule_match_run))
        if (rule_match_end == False):
            print ("Line | {:3d} | Rule Match End".format(i))
            if (rule_match_run != False):
                removal = "no " +str(running_acl[rule_match_run][0])
                acl_update.append(removal)
                del(running_acl[rule_match_run[0]])
        if (rule_match_run == False):
            print ("Line | {:3d} | Rule Match Run".format(i))
            if (rule_match_end != False):
                prev_seq = running_acl[i-1][0]
                new_seq = prev_seq + 1
                if (running_acl[i][0]>new_seq):
                    addition = str(new_seq) + " " + end_acl[i]
                    acl_update.append(addition)
                    running_acl.insert(i, [new_seq,end_acl[i]])
        if ((rule_match_run != False) and (rule_match_end != False)):
            prev_seq = running_acl[i-1][0]
            new_seq = prev_seq + 1
            addition = str(new_seq) + " " + end_acl[i]
            removal = "no " +str(running_acl[rule_match_run[0]][0])
            acl_update.append(removal)
            acl_update.append(addition)
            running_acl.insert(i, [new_seq,end_acl[i]])
            del(running_acl[rule_match_run[0]])
            i+=1
        if (rule_match_run):
            matching_rule = running_acl[rule_match_run[0]]
            # Print command for debug
            print ("Line | {:3d} | Found matching rule on line: {} | {}".format(i,rule_match_run,matching_rule))
                
                
            # Print command for debug
            #print ("Line | {:3d} | Try execution path failed, new rule line.".format(i))
            # Print command for debug
            #print ("Line | {:3d} | Insert rule {} between {} and {}.".format(i,end_acl[i],running_acl[i-num_offset][0],running_acl[i-num_offset-1][0]))
            if (running_acl[i][0]+1 < running_acl[i-1][0]):
                rule = str(running_acl[i][0]+1) + " " + end_acl[i]
                acl_update.append(rule)
        rule_match = False
        rule_match_end = False
        rule_match_run = False
print (acl_update)

num_offset = 0
i = 9
#acl_update = []
rule_match = False
while i < len(running_acl)-1:
    
    try:
        line = (end_acl.index(running_acl[i][1]))
        print ("Line | {:3d} | Rule matched {}, ignoring line".format(i, line))
    except:
        print ("Exception triggered")
        rule_delete = "no " + str(running_acl[i][0])
        acl_update.append(rule_delete)
    rule_match = False
    i+=1
