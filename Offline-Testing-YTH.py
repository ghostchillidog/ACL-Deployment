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

