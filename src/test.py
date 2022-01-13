#!/bin/usr/env python3

"""test just another easy tcp server"""

import ectc
import time
import sys

s1=None
doit = True

def cb(t):
  if isinstance(t,bytes):
    t=t.decode()
  print(t)
  if t.strip() == "r?":
    # breakpoint()
    if s1 and s1.is_connected:
      s1.send("hi\r\n")
  if t.strip() == "quit!":
    s1.send("bye!")
    s1.doit = False
      
def cbErr(t):
  print(t)

# main
# breakpoint()
s1 = ectc.server(8888)
s1.callback_rx = cb
s1.callback_err = cbErr

while not s1.is_connected:
  time.sleep(.5)
print("connected", s1.client, s1.address)

while(s1.is_connected):
  s1.send("test.")
  time.sleep(5)

print("join")
s1._thread_rx.join()
print("done.")
