#################################
##  Import required libraries  ##
#################################
from getpass import getpass
from datetime import datetime
from netmiko import ConnectHandler
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

def process_acl(connection, current_acl, new_acl):
    i=0
    A_loc = False
    B_loc = False
    update_commands = []
    rule_numbers = []
    if (len(current_acl)>len(new_acl)):
        print ("Updated ACL longer. Iterating on new_acl")
        while i <= len(new_acl):
            if ("remark" not in new_acl[i]):
                if (new_acl[i] == current_acl[i][1]):
                    print ("{:3d} | Lines equal, moving along".format(i))
                    i+=1
                else:
                    try:
                        B_loc = index_2d(current_acl,new_acl[i])
                    except ValueError:
                        print ("{:3d} | Rule from new_acl does not exist in current_acl. Rule needs adding".format(i))
                        if (i>0):
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                                i-=1
                            else:
                                print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                                acl_renumber(current_acl,10,10)
                                update_commands.append("RENUMBER ACL")
                                i=0
                        else:
                            tmp_command = str(current_acl[i][0]-1) + " " + new_acl[i]
                    try:
                        A_loc = new_acl.index(current_acl[i][1])
                    except ValueError:
                        print ("{:3d} | Rule from current_acl does not exist in new_acl. Rule needs removing".format(i))
                        tmp_command = "no " + str(current_acl[i][0])
                        update_commands.append(tmp_command)
                        del(current_acl[i])
                        if (i>0):
                            i-=1
                    if (A_loc and B_loc):
                        print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                        if (i>0):
                            print("{:3d} | i > 0. Collating rule numbers for re-order".format(i))
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                print("{:3d} | Preparing update removal: {}".format(i,B_loc))
                                tmp_command = "no " + str(current_acl[B_loc[0]][0])
                                update_commands.append(tmp_command)
                                print("{:3d} | Performing deletion from current_acl".format(i))
                                del(current_acl[B_loc[0]])
                                print("{:3d} | Preparing update addition: {}".format(i,rule_numbers))
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                print("{:3d} | Preparing running rules addition: {}".format(i,rule_numbers))
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                                i-=1
                            else:
                                print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
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
                print("{:3d} | Reached remark line, terminating".format(i))
                i+=10
    else:
        print ("Updated ACL longer. Iterating on current_acl")
        while i <= len(current_acl):
            if ("remark" not in new_acl[i]):
                if (new_acl[i] == current_acl[i][1]):
                    print ("{:3d} | Lines equal, moving along".format(i))
                    i+=1
                else:
                    try:
                        B_loc = index_2d(current_acl,new_acl[i])
                    except ValueError:
                        print ("{:3d} | Rule from new_acl does not exist in current_acl. Rule needs adding".format(i))
                        if (i>0):
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                            else:
                                print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
                                acl_renumber(current_acl,10,10)
                                update_commands.append("RENUMBER ACL")
                                i=0
                        else:
                            tmp_command = str(current_acl[i][0]-1) + " " + new_acl[i]
                    try:
                        A_loc = new_acl.index(current_acl[i][1])
                    except ValueError:
                        print ("{:3d} | Rule from current_acl does not exist in new_acl. Rule needs removing".format(i))
                        tmp_command = "no " + str(current_acl[i][0])
                        update_commands.append(tmp_command)
                        del(current_acl[i])
                        if (i>0):
                            i-=1
                    if (A_loc and B_loc):
                        print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                        if (i>0):
                            print("{:3d} | i > 0. Collating rule numbers for re-order".format(i))
                            rule_numbers = [current_acl[i-1][0],current_acl[i][0]]
                            if (rule_numbers[1]>(rule_numbers[0]+1)):
                                print("{:3d} | Preparing update removal: {}".format(i,B_loc))
                                tmp_command = "no " + str(current_acl[B_loc[0]][0])
                                update_commands.append(tmp_command)
                                print("{:3d} | Performing deletion from current_acl".format(i))
                                del(current_acl[B_loc[0]])
                                print("{:3d} | Preparing update addition: {}".format(i,rule_numbers))
                                tmp_command = str(rule_numbers[0]+1) + " " + new_acl[i]
                                update_commands.append(tmp_command)
                                print("{:3d} | Preparing running rules addition: {}".format(i,rule_numbers))
                                tmp_command = [rule_numbers[0]+1, new_acl[i]]
                                current_acl.insert(i, tmp_command)
                                i-=1
                            else:
                                print ("{:3d} | Error, cannot insert rule before line. Renumbering ACL.".format(i))
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
                print("{:3d} | Reached remark line, terminating".format(i))
                i+=10
    return update_commands

#################################
## Read in test resultant ACL  ##
#################################
file = ".\\Test-20190612-1030.txt"
acl_file = open(file,"r")
new_acl = acl_file.read()
#################################
## Define SSH connection to    ##
## test switch                 ##
#################################
ip = '192.168.6.243'
ydh_pw = getpass("Enter SNS5000 password: ")
ydh = {'device_type': 'cisco_ios', 'ip': ip, 'username': 'sns5000', 'password': ydh_pw, 'secret': ydh_pw, 'port': 22,}
acl_name = 'SMB_ACL'
#################################
## Connect to remote swtich    ##
## and enter enable mode       ##
#################################
remote_conn = ConnectHandler(**ydh)
remote_conn.enable()
#################################
## Call for ACL to be reseq    ##
## to expand number range and  ##
## reduce collisions in large  ##
## update/re-order             ##
#################################
ios_cmd = resequence_acl(acl_name, 10, 30)
result = remote_conn.send_config_set(ios_cmd)
output = remote_conn.send_command_expect("show access-list " + str(acl_name))
#################################
## Format ACL entities using   ##
## preconfigured subroutines   ##
#################################
A = format_acl(new_acl)
B = format_output(output)
#################################
## Test that remote connnect   ##
## is still connected [debug]  ##
#################################
if not (remote_conn.is_alive()):
    remote_conn = ConnectHandler(**ydh)
#################################
## Make sure in enable mode    ##
#################################
remote_conn.enable()
#################################
ios_cmds = process_acl(remote_conn, B, A)
ios_cmds.insert(0, "ip access-list extended " + str(acl_name))
result = remote_conn.send_config_set(ios_cmds)
ios_cmd = resequence_acl(acl_name, 10, 10)
result = remote_conn.send_config_set(ios_cmd)
#################################
## Disconnect SSH session      ##
#################################
remote_conn.disconnect()
#####################################
## Generate timestamp and format   ##
#####################################
tnow = datetime.now()
print (tnow.strftime("%d/%m/%Y %H:%M"))