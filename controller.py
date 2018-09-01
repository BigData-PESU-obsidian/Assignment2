import time
import sys
from kazoo.client import KazooClient

zk = KazooClient(hosts="127.0.0.1:2181")
zk.start()

try:
    zk.create("/assignment2")
except Exception:
    pass

zk.create("/assignment2/lck",
          ephemeral=True,
          sequence=True)

print("Made the first seq znode.. start dynamic.py now")

start = False

while(not start):
    ans = input("Start simulation?(y/n) ")
    if(ans == "y"):
        zk.stop()
        start = True
    else:
        pass

stop = False

while(not stop):
    ans = input("Stop simulation?(y/n) ")
    if(ans == "y"):
        zk.start()
        zk.delete("/assignment2", recursive=True)
        stop = True
    else:
        pass
