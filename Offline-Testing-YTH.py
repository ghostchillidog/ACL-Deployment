def index_2d(data, search):
    for i, e in enumerate(data):
        try:
            return i, e.index(search)
        except ValueError:
            pass
    raise ValueError("{} is not in list".format(repr(search)))

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

i=0
A_loc = False
B_loc = False

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
                try:
                    A_loc = A.index(B[i][1])
                except ValueError:
                    print ("{:3d} | Rule from B does not exist in A. Rule needs removing".format(i))
                if (A_loc and B_loc):
                    print("{:3d} | Lines not equal, but exist in both rules. Requires re-oder. Old: {:3d} | New: {:3d}".format(i,B_loc[0],A_loc))
                i+=1
                A_loc = False
                B_loc = False
        else:
            print("{:3d} | Reached remark line, terminating".format(i))
            i+=10
else:
    print ("Updated ACL longer. Iterating on B")


#
#try:
#    mylist_loc = index_2d(B,A[8])
#except ValueError:
#    print ("ValueError raised. Text does not exist in array")
#
#if (mylist_loc):
#    print ("Text located at: {}".format(mylist_loc))
#    mylist_loc = False

