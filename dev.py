import os
import time
import sys
from kazoo.client import KazooClient
'''
currval = int(sys.argv[1])
sys.argv[1] = str(currval + 1)
'''

# Starting a new process
#print("I am {} created at {}".format(os.getpid(), time.strftime('%X %x %Z')))

client = KazooClient(hosts="127.0.0.1:2181")
client.start()
#print("Kazoo client ID {}".format(client.client_id))

# CODE HERE

retval = client.create("/assignment2/lck", ephemeral = True, sequence = True).split("/")[2]
#print(retval)
#xlst = [int(val[3:]) for val in lst]

isMaster = False

def masterFun():
    pid = os.fork()
    if(pid < 0):
        print("Encountered error")

    elif(pid == 0):
        exec(open("dev.py").read(), {'isMaster':False})
        
    else:
        print("New master {}".format(retval))
        i = 0
        while(i < 2):
            #print("master alive for {} seconds".format(i))
            time.sleep(1)
            i += 1
        print("parent about to exit")
        global isMaster
        isMaster = True
        client.delete("/assignment2/"+retval)

    return(0)
        
def onElection(election):

    lst = client.get_children("/assignment2")
    lst.sort()
    if(lst[0] == retval):
        #print("old master died")
        masterFun()
    else:
        print("put watch on new master")
        client.get("/assignment2/"+lst[0], watch = onElection)

    return(0)
        
lst = client.get_children("/assignment2")
lst.sort()
print(lst)
client.get("/assignment2/"+lst[0], watch = onElection)

while(not isMaster):
    #print("This is process {}".format(os.getpid()))
    time.sleep(1)

print("the value of isMaster is 1")
