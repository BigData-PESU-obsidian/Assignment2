import os
import time
import sys
import subprocess
from kazoo.client import KazooClient

# Initial connection establishment
client = KazooClient(hosts="127.0.0.1:2181")
client.start()

# create an ephemeral , sequence znode and get its name
isMaster = False
retval = client.create("/assignment2/lck",
                       ephemeral=True,
                       sequence=True).split("/")[2]


def masterFun1():
    """
    This is the function thats called as soon as one process becomes the
    master

    WORKING : This creates a new process which again runs the same program
              and after creation, the current master program terminates
              after 1 second, thus releasing the lock and letting a new
              process take over and continue
    """

    p = subprocess.Popen(['python', 'dynamic.py'])
    print("New master {}".format(retval))
    i = 0
    while(i < 1):
        time.sleep(1)
        i += 1
    global isMaster
    isMaster = True
    client.delete("/assignment2/"+retval)


def onElection(election):
    """
    This is the listner function called on each of the non-master processes
    as soon as the current master dies.

    WORKING : This checks if the current process' retval (the node id) is
              equal to the minimum thats present or not.
              if the current retval is equal to the minimum present in the
              list of sequential children nodes, then this function calls
              the above mentioned masterFun function else it resets its watcher
              on the current minimum znode.
    """
    lst = client.get_children("/assignment2")
    lst.sort()
    if(lst[0] == retval):
        masterFun1()
    else:
        client.get("/assignment2/"+lst[0], watch=onElection)
    return(0)


onElection(None)

# Busy wait for chance to become next master
while(not isMaster):
    time.sleep(1)
