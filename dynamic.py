import os
import time
import sys
import subprocess
from kazoo.client import KazooClient
from kazoo.client import KazooState

try:
    # Initial connection establishment
    client = KazooClient(hosts="127.0.0.1:2181")
    client.start()

    # If to stop the simulation
    stop = bool(int.from_bytes(client.get("/stop")[0], byteorder="little"))
    if(stop):
        exit(0)

    def clientListner(state):
        """
        This is a listner added to the client to handle what happens when there
        is a failure

        WORKING : exits safely on disconnection or on losing session from the
                  ZooKeeper process
        """

        if(state == KazooState.LOST):
            print("Client {} lost session from ZooKeeper".format(os.getpid()))
            exit(0)
        elif(state == KazooState.SUSPENDED):
            print("Client {} disconnected from ZooKeeper".format(os.getpid()))
            exit(0)
        else:
            print("State of Client {} changed".format(os.getpid()))

    client.add_listener(clientListner)

    # create an ephemeral , sequence znode and get its name
    isMaster = False
    nodePath = client.create("/assignment2/lck", ephemeral=True, sequence=True)

    retval = nodePath.split("/")[2]
    client.set(nodePath, bytes([os.getpid() % 256]))

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
        print("New master node is {}".format(retval))
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

        WORKING : This checks if the current process' sequence number is
                  equal to the minimum thats present or not.
                  if the current sequence number is equal to the minimum
                  present in the list of sequential children nodes, then
                  this function calls the above mentioned masterFun
                  function else it resets its watcher on the current
                  minimum znode.
        """

        lst = [(int.from_bytes(client.get("/assignment2/"+child)[0],
                               byteorder="little"), child)
               for child in client.get_children("/assignment2")]
        lst.sort(key=lambda x: x[1])

        # if(lst[0][0] == (os.getpid() % 256)):
        if(lst[0][1] == retval):
            masterFun1()
        else:
            client.get("/assignment2/"+lst[0][1], watch=onElection)
        return(0)

    onElection(None)
    stop = False

    # Busy wait for chance to become next master
    while(not isMaster):
        time.sleep(1)

except Exception:
    print("Stopping")
    exit(0)
