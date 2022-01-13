# by g1

"""just another easy tcp server and client"""

__version__ = "0.1.2"

import socket
import threading
import time


class server:
  """easy tcp server"""
  verbosity = 1 # 0=nothing, 1=error, 2=warning, 3=info, 4=more info
  sock = None
  port = None
  host = "localhost"
  lastError = None
  doit = True
  buf_size = 1024
  callback_rx = None
  callback_error = None
  onconnect = None
  onclose = None
  udp = None
  _thread_rx = None
  client = None
  max_clients_num = 1
  is_connected = False
  
  def __init__(self, port, host=None, listen=True):
    """call with listening port, optional host, listen is default=True"""
    if host:
      self.host = host
    self.port = port
    self.sock = None
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.setblocking = None

      self._thread_rx = threading.Thread(target=self._rxthread)  # args=[self]
      if listen:
        self.listen()
      else:
        self.is_connected = False
    except Exception as e:
      self.sock = None
      if self.verbosity:
        print("server create error: ",e)
      self.lastError = str(e)

  def listen(self):
    """call manually, if creation of server was with listen=False"""
    self.is_connected = False
    self.doit = True
    self._thread_rx.start()

  def send(self, data):
    try:
      if not isinstance(data,bytes):
        data = data.encode()
      self.connection.sendall(data)
    except Exception as e:
      if self.verbosity:
        print("tx err: "+str(e))

  # def is_connected(self):
  #   #if not self._thread_rx.running
  #   return self.is_connected

  def close(self):
    self.doit = False
    if self.sock:
      self.sock.close()
    self.is_connected = False
    if self.onclose:
      self.onclose()

  def _rxthread(self):
    while self.doit and not self.is_connected:
      try:
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.connection, self.address = self.sock.accept()
        self.is_connected = True
        self.onconnect and self.onconnect()
      except Exception as e:
        if self.verbosity:
          print("bind error! "+str(e))
        self.callback_error and self.callback_error()
        time.sleep(.3)

    while self.doit:
      # breakpoint()
      try:
        rxd = self.connection.recv(self.buf_size)
        if rxd and self.callback_rx:
          self.callback_rx(rxd)
        elif not rxd:
          self.doit = 0
      except Exception as e:
        self.sock = None
        if self.verbosity: print("server create error: ", e)
        self.callback_error and self.callback_error("rx error: "+str(e))
        self.doit = 0
    self.close()

  def __del__(self):
    self.close()


class client:
  """easy tcp socket"""
  verbosity = 1 # 0=nothing, 1=error, 2=warning, 3=info, 4=more info
  sock = None
  port = None
  host = "localhost"
  lastError = None
  doit = True
  buf_size = 1024
  callback_rx = None
  callback_error = None
  udp = None
  _thread_rx = None
  is_connected = False
  _rxdata = b""
  _lock = False
  
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = None
    self.is_connected = False
    # self._thread_rx = threading.Thread(target=self._rxthread)
    self.connect()

  def connect(self, timeout=1):
    """try connect with timeout in seconds"""
    if self.is_connected:
      return False
    if self._thread_rx and _thread_rx.isAlive():
      return False
    self._thread_rx = threading.Thread(target=self._rxthread)
    try:
      self.sock = socket.create_connection((self.host, self.port))
      self.sock.setblocking(False)
    except Exception as e:
      self.sock = None
      self.lastError = "can't connect: "+str(e)
      if self.verbosity:
        print(self.lastError)
      return False
    self._thread_rx.start()

  def send(self, data):
    try:
      if not isinstance(data,bytes):
        data = data.encode()
      self.sock.sendall(data)
    except Exception as e:
      if self.verbosity:
        print("tx err: "+str(e))

  # def is_connected(self):
  #   #if not self._thread_rx.running
  #   return self.is_connected

  def close(self):
    self.doit = False
    if self.sock:
      self.sock.close()
    self.is_connected = False

  def _rxthread(self):
    self.doit = True
    while self.doit:
      if not self.callback_rx:
        time.sleep(.5)
        continue
      # breakpoint()
      try:
        rxd = self.sock.recv(self.buf_size)
        if not rxd:
          elf.doit = 0
        elif self.callback_rx:
          self.callback_rx(rxd)
        else:
          self.rxdata += rxd
      except Exception as e:
        if e.args[0] == 11:  # Resource temporarily unavailable
          pass
        elif self.verbosity:
          print("server read error: ", e)
          if self.callback_error:
            self.callback_error("rx error: "+str(e))
          self.doit = 0
    self.close()

  def recv(self, maxbytes):
    if 0:
      r = self._rxdata[:maxbytes]
      self._rxdata = self._rxdata[maxbytes:]
      return r
    else:
      try:
        r = self.sock.recv(maxbytes)
        return r
      except Exception as e:
        if e.args[0] == 11:  # Resource temporarily unavailable
          pass
        elif self.verbosity:
          print("server read error: ", e)
          if self.callback_error:
            self.callback_error("rx error: "+str(e))

  def __del__(self):
    self.close()

#eof
