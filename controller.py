import time
import sys
import os
from kazoo.client import KazooClient

zk = KazooClient(hosts="127.0.0.1:2181")
zk.start()

try:
    zk.create("/assignment2")
    zk.create("/stop")
except Exception:
    pass

nd = zk.create("/assignment2/lck", ephemeral=True, sequence=True)

zk.set(nd, bytes([os.getpid() % 256]))
zk.set("/stop", bytes([0]))

print("Made the first seq znode.. start dynamic.py now")
start = False

while(not start):
    ans = input("Start simulation?(y/n) ")
    if(ans == "y"):
        zk.set("/stop", bytes([0]))
        zk.stop()
        start = True
    else:
        pass

stop = False

while(not stop):
    ans = input("Stop simulation?(y/n) ")
    if(ans == "y"):
        zk.start()
        zk.set("/stop", bytes([1]))
        #zk.delete("/assignment2", recursive = True)
        #zk.delete("/stop", recursive = True)
        stop = True
    else:
        pass
