#################################
##  Import required libraries  ##
#################################
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
#from acl import new_server as new_server
from acl import acl as acl_template
tstart = datetime.now()
#################################
## Subroutine for 2D array search ##
#################################
def index_2d(data, search):
    for i, e in enumerate(data):
        try:
            return i, e.index(search)
        except ValueError:
            pass
    raise ValueError("{} is not in list".format(repr(search)))
#################################
## Define subroutine to format ##
## output from SSH into neater ##
## text variable               ##
#################################
def format_output(output):
    temp_acl = output.split('\n')
    if ("Extended IP access list" in temp_acl[0]):
        del(temp_acl[0])
    B = []
    for row in temp_acl:
        tmp = row.replace("   "," ")
        tmp = tmp.replace("  "," ")
        tmp = tmp.lstrip().rsplit(" (")[0].split(" ",1)
        tmp[0] = int(tmp[0])
        B.append(tmp)
    B.append([tmp[0]+30, "remark End of ACL"])
    return B
#################################
## Define subroutine to format ##
## output from ALC import      ##
## into parsable  variable     ##
#################################
def format_acl(acl):
    temp_acl = acl.split('\n')
    A = []
    for row in temp_acl:
        tmp = row.rstrip()
        if not (tmp == ''):
            A.append(tmp)
    return A

def resequence_acl(acl_name, start, increment):
    ios_cmd ="ip access-list resequence " + str(acl_name) + " " + str(start) + " " + str(increment)
    return (ios_cmd)

def process_acl(current_acl, new_acl):
    i=0
    A_loc = False
    B_loc = False
    update_commands = []
    rule_numbers = []
    if (len(current_acl)>len(new_acl)):
        #print ("Updated ACL longer. Iterating on new_acl")
        while i <= len(new_acl):
            if ("remark" not in new_acl[i]):
                if (new_acl[i] == current_acl[i][1]):
                    #print ("{:3d} | Lines equal, moving along".format(i))
                    i+=1
                else:
                    try:
                        B_loc = index_2d(current_acl,new_acl[i])
                    except ValueError:
                        #print ("{:3d} | Rule from new_acl does not exist in current_acl. Rule needs adding".format(i))
                        if (i>0):
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                                i-=1
                            else:
                                #print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                                acl_renumber(current_acl,10,10)
                                update_commands.append("RENUMBER ACL")
                                i=0
                        else:
                            tmp_command = str(current_acl[i][0]-1) + " " + new_acl[i]
                    try:
                        A_loc = new_acl.index(current_acl[i][1])
                    except ValueError:
                        #print ("{:3d} | Rule from current_acl does not exist in new_acl. Rule needs removing".format(i))
                        tmp_command = "no " + str(current_acl[i][0])
                        update_commands.append(tmp_command)
                        del(current_acl[i])
                        if (i>0):
                            i-=1
                    if (A_loc and B_loc):
                        #print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                        if (i>0):
                            #print("{:3d} | i > 0. Collating rule numbers for re-order".format(i))
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                #print("{:3d} | Preparing update removal: {}".format(i,B_loc))
                                tmp_command = "no " + str(current_acl[B_loc[0]][0])
                                update_commands.append(tmp_command)
                                #print("{:3d} | Performing deletion from current_acl".format(i))
                                del(current_acl[B_loc[0]])
                                #print("{:3d} | Preparing update addition: {}".format(i,rule_numbers))
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                #print("{:3d} | Preparing running rules addition: {}".format(i,rule_numbers))
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                                i-=1
                            else:
                                #print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                                acl_renumber(current_acl,10,10)
                                update_commands.append("RENUMBER ACL")
                                i=0
                        else:
                            tmp_command = str(current_acl[i][0]-1) + " " + new_acl[i]
                            update_commands.append(tmp_command)
                            tmp_command = [current_acl[i][0]-1, new_acl[i]]
                            current_acl.insert(i, tmp_command)
                            tmp_command = "no " + str(current_acl[B_loc][0])
                            update_commands.append(tmp_command)
                            del(current_acl[B_loc[0]])
                    A_loc = False
                    B_loc = False
            else:
                #print("{:3d} | Reached remark line, terminating".format(i))
                i+=10
    else:
        #print ("Updated ACL longer. Iterating on current_acl")
        while i <= len(current_acl):
            if ("remark" not in new_acl[i]):
                if (new_acl[i] == current_acl[i][1]):
                    #print ("{:3d} | Lines equal, moving along".format(i))
                    i+=1
                else:
                    try:
                        B_loc = index_2d(current_acl,new_acl[i])
                    except ValueError:
                        #print ("{:3d} | Rule from new_acl does not exist in current_acl. Rule needs adding".format(i))
                        if (i>0):
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                            else:
                                #print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                                acl_renumber(current_acl,10,10)
                                update_commands.append("RENUMBER ACL")
                                i=0
                        else:
                            tmp_command = str(current_acl[i][0]-1) + " " + new_acl[i]
                    try:
                        A_loc = new_acl.index(current_acl[i][1])
                    except ValueError:
                        #print ("{:3d} | Rule from current_acl does not exist in new_acl. Rule needs removing".format(i))
                        tmp_command = "no " + str(current_acl[i][0])
                        update_commands.append(tmp_command)
                        del(current_acl[i])
                        if (i>0):
                            i-=1
                    if (A_loc and B_loc):
                        #print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                        if (i>0):
                            #print("{:3d} | i > 0. Collating rule numbers for re-order".format(i))
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                #print("{:3d} | Preparing update removal: {}".format(i,B_loc))
                                tmp_command = "no " + str(current_acl[B_loc[0]][0])
                                update_commands.append(tmp_command)
                                #print("{:3d} | Performing deletion from current_acl".format(i))
                                del(current_acl[B_loc[0]])
                                #print("{:3d} | Preparing update addition: {}".format(i,rule_numbers))
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                #print("{:3d} | Preparing running rules addition: {}".format(i,rule_numbers))
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                                i-=1
                            else:
                                #print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                                acl_renumber(current_acl,10,10)
                                update_commands.append("RENUMBER ACL")
                                i=0
                        else:
                            tmp_command = str(current_acl[i][0]-1) + " " + new_acl[i]
                            update_commands.append(tmp_command)
                            tmp_command = [current_acl[i][0]-1, new_acl[i]]
                            current_acl.insert(i, tmp_command)
                            tmp_command = "no " + str(current_acl[B_loc][0])
                            update_commands.append(tmp_command)
                            del(current_acl[B_loc[0]])
                    A_loc = False
                    B_loc = False
            else:
                #print("{:3d} | Reached remark line, terminating".format(i))
                i+=10
    return update_commands

#################################
## Read in test resultant ACL  ##
#################################
#file = ".\\Test-20190612-1030.txt"
#acl_file = open(file,"r")
#new_acl = acl_file.read()
#################################
## Define SSH connection to    ##
## test switch                 ##
#################################
#ip = '192.168.6.243'
#ydh_pw = getpass("Enter SNS5000 password: ")
#ydh = {'device_type': 'cisco_ios', 'ip': ip, 'username': 'sns5000', 'password': ydh_pw, 'secret': ydh_pw, 'port': 22,}
#acl_name = 'SMB_ACL'
#################################
## Connect to remote swtich    ##
## and enter enable mode       ##
#################################
#remote_conn = ConnectHandler(**ydh)
#remote_conn.enable()
#################################
## Call for ACL to be reseq    ##
## to expand number range and  ##
## reduce collisions in large  ##
## update/re-order             ##
#################################
#ios_cmd = resequence_acl(acl_name, 10, 30)
#tresequence = datetime.now()
#result = remote_conn.send_config_set(ios_cmd)
#output = remote_conn.send_command_expect("show access-list " + str(acl_name))
#print("\nResequence elapsed time: " + str(datetime.now() - tresequence))
#################################
## Format ACL entities using   ##
## preconfigured subroutines   ##
#################################
#A = format_acl(new_acl)
#B = format_output(output)
#################################
## Test that remote connnect   ##
## is still connected [debug]  ##
#################################
#if not (remote_conn.is_alive()):
#    remote_conn = ConnectHandler(**ydh)
#################################
## Make sure in enable mode    ##
#################################
#remote_conn.enable()
#################################
#tprocess = datetime.now()
#ios_cmds = process_acl(B, A)
#print("\nACL processing elapsed time: " + str(datetime.now() - tprocess))
#ios_cmds.insert(0, "ip access-list extended " + str(acl_name))
#tupdate_acl = datetime.now()
#result = remote_conn.send_config_set(ios_cmds)
#print("\nACL update elapsed time: " + str(datetime.now() - tupdate_acl))
#Get-NetworkControllerLoadBalancerMux
#tend_resequence = datetime.now()
#result = remote_conn.send_config_set(ios_cmd)
#print("\nFinal resequence elapsed time: " + str(datetime.now() - tend_resequence))
#################################
## Disconnect SSH session      ##
#################################
#remote_conn.disconnect()
#####################################
## Generate timestamp and format   ##
#####################################
#tnow = datetime.now()
#print (tnow.strftime("%d/%m/%Y %H:%M"))
#print("\nElapsed time: " + str(datetime.now() - tstart))

def getap(q,r,s,t, result, acl_template):
    '''Execute show version command using Netmiko.'''
    while not q.empty():
        work = q.get()
        site = r.get()
        index = int(s.get())
        acl = t.get()
        lock = threading.Lock()
        ios_cmd = []
        ios_cmds = []
        try:
            remote_conn = ConnectHandler(**work)
            switchprompt = remote_conn.find_prompt()[:-1]
            print ("Processing {}. {} [{}]".format(index, switchprompt, work['ip']))
            #switchprompt = "DebugSwitch"+str(index)
            remote_conn.enable()
            print ("Processing {}. Peforming ACL resequence.".format(switchprompt))
            ios_cmd = resequence_acl(acl, 10, 30)
            resquence_output = remote_conn.send_config_set(ios_cmd)
            print ("Processing {}. Gathering running ACL.".format(switchprompt))
            output = remote_conn.send_command_expect("show access-list " + str(acl))
            print ("Processing {}. Formatting running ACL for processing.".format(switchprompt))
            B = format_output(output)
            ios_cmds = process_acl(B, acl_template)
            print ("Processing {}. ACL processing completed.".format(switchprompt))
            print ("Output:\n {}".format(ios_cmds))
            if (len(ios_cmds) > 0):
                ios_cmds.insert(0, "ip access-list extended " + str(acl))
                ios_cmds.append(resequence_acl(acl, 10, 10))
                print ("Processing {}. Peforming ACL updates.".format(switchprompt))
                update_result = remote_conn.send_config_set(ios_cmds)
                print ("Processing {}. Writing running-memory.".format(switchprompt))
                remote_conn.send_command_expect("wr mem")
                updated = True
            else:
                print ("Processing {}. No changes required.".format(switchprompt))
                ios_cmds = resequence_acl(acl, 10, 10)
                print ("Processing {}. Peforming ACL resequence to standard.".format(switchprompt))
                update_result = remote_conn.send_config_set(ios_cmds)
                print ("Processing {}. Writing running-memory.".format(switchprompt))
                remote_conn.send_command_expect("wr mem")
                updated = False
            remote_conn.disconnect()
            if (updated):
                update = [work['ip'],switchprompt,acl,ios_cmds,updated,site]
            else:
                update = [work['ip'],switchprompt,acl,"No changes",updated,site]
            
        except:
            update = [work['ip'],"Error","Error","Error","Error",site]
            print("Error in connection for IP: {}".format(work['ip']))
        lock.acquire()
        try:
            print ("Update:\n{}".format(update))
            print ("Process: {}\nResult:\n{}".format(index,result))
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
    new_acl = format_acl(acl_template)
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
        worker = threading.Thread(target=getap, args=(q,r,s,t,results,new_acl))
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
