import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import csv
import threading
import queue
from datetime import datetime
from netmiko import ConnectHandler
from my_devices import device_acl as acl
from my_devices import device_list as devices
from my_devices import device_location as location
from my_devices import headers as headers
from acl import new_server as new_server
from acl import acl as acl_template

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
