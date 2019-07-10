def index_2d(data, search):
    for i, e in enumerate(data):
        try:
            return i, e.index(search)
        except ValueError:
            pass
    raise ValueError("{} is not in list".format(repr(search)))

running_acl_file = "Test-20181203-1400.txt"
new_acl_file = "Test-20190612-1030.txt"
A = open(new_acl_file).readlines()
B = open(running_acl_file).readlines()

AA = []
BB = []

for row in A:
    tmp = row.rstrip()
    AA.append(tmp)

i=10

output_run_array = []
for row in B:
    tmp = row.replace("access-list 150 ", "")
    tmp = tmp.rstrip()
    tmp = tmp.replace("   "," ")
    tmp = tmp.replace("  "," ")
    tmp2 = [i, tmp]
    BB.append(tmp2)
    i+=10

loc_A = False
loc_b = False
if (len(AA)>len(BB)):
    print ("New ACL longer. Iterating variable A")
    i=0
    while (i < len(AA)):
        if (AA[i] == BB[i][1]):
            print ("{} | Lines match, moving on to next line".format(i))
            i+=1
        else:
            if ("remark" in A[i]):
                print ("Skipping line - remark")
            print ("{} | Line mismatch. Testing Case".format(i))
            loc_A = AA.index(BB[i][1])
            loc_B = index_2d(BB,AA[i])
            if (loc_A and loc_B):
                print ("Line found in both arrays. Reorder")
                print ("A: {} | B: {}".format(loc_A,loc_B[0]))
            else:
                if (loc_A):
                    print ("A: {} | Add to B".format(loc_A))
                if (loc_B):
                    print ("Remove B line {}".format(loc_B[0]))
            i+=1
        loc_A = False
        loc_B = False
else:
    print ("Running ACL longer. Iterating variable B")
    if ("remark" in B[i][1]):
        print ("Skipping line - remark")
