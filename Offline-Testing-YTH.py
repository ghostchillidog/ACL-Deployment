import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import csv
import threading
import queue
from getpass import getpass
from datetime import datetime
from netmiko import ConnectHandler
from my_devices import device_acl as acl
from my_devices import device_list as devices
from my_devices import device_location as location
from my_devices import headers as headers

def index_2d(data, search):
    for i, e in enumerate(data):
        try:
            return i, e.index(search)
        except ValueError:
            pass
    raise ValueError("{} is not in list".format(repr(search)))

def acl_renumber(data, initial, increment):
    i = initial
    for row in data:
        row[0] = i
        i+=increment

def getap(q,r,s,t, result):
    '''Execute show version command using Netmiko.'''
    while not q.empty():
        work = q.get()
        site = r.get()
        index = s.get()
        acl = t.get()
        lock = threading.Lock()
        try:
            remote_conn = ConnectHandler(**work)
            switchprompt = remote_conn.find_prompt()[:-1]
            #switchprompt = "DebugSwitch"+str(index)
            remote_conn.enable()
            output = remote_conn.send_command_expect("show running-config | include access-list " + str(acl))
            #output = "Test"
            # if ([not] new_server in output): -> ## Command to check if text exists in a variable
            if (new_server in output):
                updated = False
            else:
                new_acl = acl_template.replace("%ACL%",acl)
                remote_conn.send_command_expect(new_acl)
                #print ("Debug entry, output ACL to screen")
                #print (new_acl)
                #print ("end entry")
                remote_conn.send_command_expect("wr mem")
                updated = True
            print ("Processing {}. {} [{}]".format(index, switchprompt, work['ip']))
            remote_conn.disconnect()
            if len(output) == 0:
                update = [work['ip'],switchprompt,acl,"No entry",updated,site]
            else:
                update = [work['ip'],switchprompt,acl,output,updated,site]
        except:
            update = [work['ip'],"Error","Error","Error","Error",site]
            print("Error in connection for IP: {}".format(work['ip']))
        lock.acquire()
        try:
            result[index] = update
        finally:
            lock.release()
        q.task_done()
    return True

def main():
    '''
    Use threads and Netmiko to connect to each of the devices. Execute
    'show version' on each device. Record the amount of time required to do this.
    '''
    results = [{} for x in devices]
    start_time = datetime.now()
    q = queue.Queue(maxsize=0)
    r = queue.Queue(maxsize=0)
    s = queue.Queue(maxsize=0)
    t = queue.Queue(maxsize=0)
    # Use many threads (30 max, or one for each switch)
    num_theads = min(10, len(devices))
    for i in range(len(devices)):
        #need the index and the url in each queue item.
        #print("Queue initialised with: Device | {} | i | {} |".format((devices[i]), i))
        q.put(devices[i])
        r.put(location[i])
        s.put(i)
        t.put(acl[i])
    #print ("Queue initiated size is: {}".format(q.qsize()))
    for i in range(num_theads):
        worker = threading.Thread(target=getap, args=(q,r,s,t,results))
        worker.setDaemon(True)    #setting threads as "daemon" allows main program to 
                                  #exit eventually even if these dont finish 
                                  #correctly.
        worker.start()
    #now we wait until the queue has been processed
    q.join()
    ## Prepart CSV for import
    file=".\ACL_Update_Output.csv"
    with open(file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for i in range(len(results)):
            writer.writerow({'IP': results[i][0], 'Name': results[i][1], 'ACL_Number': results[i][2], 'Old_ACL': results[i][3],'Updated': results[i][4], 'Site': results[i][5]})
    print("\nElapsed time: " + str(datetime.now() - start_time))

if __name__ == "__main__":
    main()


### Notepad++ - Find/Replace: Find: '\r\n' Replace: '\\n'
### Should replace all Carriage Return/Line Feed pairs to literal '\n'
file = ".\\acl.txt"
acl_file = open(file,"r")
acl = acl_file.read()


updated_acl_file = "Test-20190612-1030.txt"
running_acl_file = "Test-20181203-1400.txt"


text1 = open(updated_acl_file).readlines()
text2 = open(running_acl_file).readlines()

A = []
for row in text1:
    tmp = row.rstrip()
    #tmp = tmp.split(" ",1)
    #tmp[0] = int(tmp[0])
    A.append(tmp)

i=10
B = []
for row in text2:
    tmp = row.rstrip()
    tmp = tmp.replace("access-list 150 ", "")
    tmp = tmp.replace("   "," ")
    tmp = tmp.replace("  "," ")
    tmp2 = [i, tmp]
    B.append(tmp2)
    i+=10


B = Backup_B.copy()

i=0
A_loc = False
B_loc = False
update_commands = []
rule_numbers = []
if (len(A)>len(B)):
    print ("Updated ACL longer. Iterating on A")
    while i <= len(A):
        if ("remark" not in A[i]):
            if (A[i] == B[i][1]):
                print ("{:3d} | Lines equal, moving along".format(i))
                i+=1
            else:
                try:
                    B_loc = index_2d(B,A[i])
                except ValueError:
                    print ("{:3d} | Rule from A does not exist in B. Rule needs adding".format(i))
                    if (i>0):
                        rule_numbers = [B[i-1][0],B[i][0]]
                        if (rule_numbers[1]>(rule_numbers[0]+1)):
                            tmp_command = str(rule_numbers[0]+1) + " " + A[i]
                            update_commands.append(tmp_command)
                            tmp_command = [rule_numbers[0]+1, A[i]]
                            B.insert(i, tmp_command)
                            i-=1
                        else:
                            print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                            acl_renumber(B,10,10)
                            update_commands.append("RENUMBER ACL")
                            i=0
                    else:
                        tmp_command = str(B[i][0]-1) + " " + A[i]
                try:
                    A_loc = A.index(B[i][1])
                except ValueError:
                    print ("{:3d} | Rule from B does not exist in A. Rule needs removing".format(i))
                    tmp_command = "no " + str(B[i][0])
                    update_commands.append(tmp_command)
                    del(B[i])
                    if (i>0):
                        i-=1
                if (A_loc and B_loc):
                    print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                    if (i>0):
                        print("{:3d} | i > 0. Collating rule numbers for re-order".format(i))
                        rule_numbers = [B[i-1][0],B[i][0]]
                        if (rule_numbers[1]>(rule_numbers[0]+1)):
                            print("{:3d} | Preparing update removal: {}".format(i,B_loc))
                            tmp_command = "no " + str(B[B_loc[0]][0])
                            update_commands.append(tmp_command)
                            print("{:3d} | Performing deletion from B".format(i))
                            del(B[B_loc[0]])
                            print("{:3d} | Preparing update addition: {}".format(i,rule_numbers))
                            tmp_command = str(rule_numbers[0]+1) + " " + A[i]
                            update_commands.append(tmp_command)
                            print("{:3d} | Preparing running rules addition: {}".format(i,rule_numbers))
                            tmp_command = [rule_numbers[0]+1, A[i]]
                            B.insert(i, tmp_command)
                            i-=1
                        else:
                            print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                            acl_renumber(B,10,10)
                            update_commands.append("RENUMBER ACL")
                            i=0
                    else:
                        tmp_command = str(B[i][0]-1) + " " + A[i]
                        update_commands.append(tmp_command)
                        tmp_command = [B[i][0]-1, A[i]]
                        B.insert(i, tmp_command)
                        tmp_command = "no " + str(B[B_loc][0])
                        update_commands.append(tmp_command)
                        del(B[B_loc[0]])
                A_loc = False
                B_loc = False
        else:
            print("{:3d} | Reached remark line, terminating".format(i))
            i+=10
else:
    print ("Updated ACL longer. Iterating on B")
    while i <= len(B):
        if ("remark" not in A[i]):
            if (A[i] == B[i][1]):
                print ("{:3d} | Lines equal, moving along".format(i))
                i+=1
            else:
                try:
                    B_loc = index_2d(B,A[i])
                except ValueError:
                    print ("{:3d} | Rule from A does not exist in B. Rule needs adding".format(i))
                    if (i>0):
                        rule_numbers = [B[i-1][0],B[i][0]]
                        if (rule_numbers[1]>(rule_numbers[0]+1)):
                            tmp_command = str(rule_numbers[0]+1) + " " + A[i]
                            update_commands.append(tmp_command)
                            tmp_command = [rule_numbers[0]+1, A[i]]
                            B.insert(i, tmp_command)
                        else:
                            print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                            acl_renumber(B,10,10)
                            update_commands.append("RENUMBER ACL")
                            i=0
                    else:
                        tmp_command = str(B[i][0]-1) + " " + A[i]
                try:
                    A_loc = A.index(B[i][1])
                except ValueError:
                    print ("{:3d} | Rule from B does not exist in A. Rule needs removing".format(i))
                    tmp_command = "no " + str(B[i][0])
                    update_commands.append(tmp_command)
                    del(B[i])
                    if (i>0):
                        i-=1
                if (A_loc and B_loc):
                    print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                    if (i>0):
                        print("{:3d} | i > 0. Collating rule numbers for re-order".format(i))
                        rule_numbers = [B[i-1][0],B[i][0]]
                        if (rule_numbers[1]>(rule_numbers[0]+1)):
                            print("{:3d} | Preparing update removal: {}".format(i,B_loc))
                            tmp_command = "no " + str(B[B_loc[0]][0])
                            update_commands.append(tmp_command)
                            print("{:3d} | Performing deletion from B".format(i))
                            del(B[B_loc[0]])
                            print("{:3d} | Preparing update addition: {}".format(i,rule_numbers))
                            tmp_command = str(rule_numbers[0]+1) + " " + A[i]
                            update_commands.append(tmp_command)
                            print("{:3d} | Preparing running rules addition: {}".format(i,rule_numbers))
                            tmp_command = [rule_numbers[0]+1, A[i]]
                            B.insert(i, tmp_command)
                            i-=1
                        else:
                            print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                            acl_renumber(B,10,10)
                            update_commands.append("RENUMBER ACL")
                            i=0
                    else:
                        tmp_command = str(B[i][0]-1) + " " + A[i]
                        update_commands.append(tmp_command)
                        tmp_command = [B[i][0]-1, A[i]]
                        B.insert(i, tmp_command)
                        tmp_command = "no " + str(B[B_loc][0])
                        update_commands.append(tmp_command)
                        del(B[B_loc[0]])
                A_loc = False
                B_loc = False
        else:
            print("{:3d} | Reached remark line, terminating".format(i))
            i+=10

print(update_commands)

#
#try:
#    mylist_loc = index_2d(B,A[8])
#except ValueError:
#    print ("ValueError raised. Text does not exist in array")
#
#if (mylist_loc):
#    print ("Text located at: {}".format(mylist_loc))
#    mylist_loc = False

