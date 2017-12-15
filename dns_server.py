#pip install dnspython
# -*- coding: utf-8 -*-
import socket
import dns.resolver
import sys
import os
import random
from shutil import copyfile
import sqlite3
import time
from datetime import datetime
from threading import Thread
import platform
global cur
global con
global lock
global bansite
global whitesite
global ip
global tm
global start
global cache1
global sqldirectory
global base
lock = 0
bansite = 0
whitesite = 0
cache1 = 0
start = 0
tm = ''
ip=''
base = os.path.abspath(os.curdir)+'\\dnsbase'
sqldirectory = os.path.abspath(os.curdir)+'\\atmsdns_data\\sql\\'
def printx(s):
        if platform.system() == 'Windows':
            print s.decode('utf-8')
        if platform.system() == 'Linux':
            print s
def sqlwriter():
    print('SQL connect to base: '+base)
    con2 = sqlite3.connect(base)
    cur2 = con2.cursor()
    while 1:
        try:
            files = os.listdir(sqldirectory)
            for file in files:
                 if '.sql' in file:
                    time.sleep(0.1)
                    sql = open(sqldirectory+file,'r')
                    sq = sql.read()
                    printx(file+' -> execute: ['+sq+']')
                    cur2.execute(sq)
                    sql.close()
                    os.remove(sqldirectory+file)
            con2.commit()
        except BaseException:
            time.sleep(2)
t1 = Thread(target=sqlwriter)
t1.start()
#t1.join()

print('DNS connect to base: '+base)
con0 = sqlite3.connect(base)
cur0 = con0.cursor()
cur0.execute('select * from job')
cr = cur0.fetchall()
lock = int(cr[0][0])
if lock == 1:
    print('Mode: blocking')
else:
    print('Mode: non-blocking')

def sqlexecute(sqltext):
    tm = datetime.strftime(datetime.now(), '%H%M%S')+str(random.randint(0, 999999999))+'.sql'
    sql = open(sqldirectory+tm,'w')
    sql.write(sqltext)
    sql.close()

class DNSQuery:
  def __init__(self, data):
    self.data=data
    self.dominio=''

    tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
    if tipo == 0:                     # Standard query
      ini=12
      lon=ord(data[ini])
      while lon != 0:
        self.dominio+=data[ini+1:ini+lon+1]+'.'
        ini+=lon+1
        lon=ord(data[ini])

  def makepacket(self, ip):
    packet=''
    if self.dominio:
      packet+=self.data[:2] + "\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+='\xc0\x0c'                                             # Pointer to domain name
      packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
    return packet

if __name__ == '__main__':
  print 'ATMSDNS loading.... %s' % ip
  sqlexecute('delete from log')
  my_resolver = dns.resolver.Resolver()
  # 8.8.8.8 and 8.8.4.4 is Google's public DNS server
  my_resolver.nameservers = ['8.8.4.4','8.8.8.8']
  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udps.bind(('',53))
  try:
     while 1:
      try:
          data, addr = udps.recvfrom(1024)
          p=DNSQuery(data)
          #in thread
          def work():
              con = sqlite3.connect(base)
              cur = con.cursor()
              cur.execute('select * from job')
              cr = cur.fetchall()
              lock = int(cr[0][0])
              bansite = 0
              c = cur.execute('select * from ban')
              for row in c.fetchall():
                  if row[0] in p.dominio:
                       bansite = 1
              whitesite = 0
              c = cur.execute("select * from white")
              for row in c.fetchall():
                  if row[0] in p.dominio:
                      whitesite = 1
              tm = datetime.strftime(datetime.now(), '%H:%M:%S')

              if ((lock==1) and (whitesite==0)) or (bansite==1):
                  ip = 'нет';
                  #udps.sendto(p.makepacket(ip), addr)
                  printx('ban>: [%s]' % (p.dominio))
                  sqlexecute('insert into log values("'+tm+'","'+ip+'","'+p.dominio+'","'+addr[0]+':'+str(addr[1])+'"," не отвечаю, запрещено.")')
                  con.commit()
              else:
                  if not 'in-addr.arpa' in p.dominio:
                      answer = my_resolver.query(p.dominio,'A')
                      for rdata in answer:
                          ip = str(rdata)
                      udps.sendto(p.makepacket(ip), addr)
                      printx(tm+' google_dns>: [%s -> %s] for %s' % (p.dominio, ip, addr[0]))
                      if cache1 == 1:
                          sqlexecute('insert into cache values("'+p.dominio+'","'+ip+'")')
                      sqlexecute('insert into log values("'+tm+'","'+ip+'","'+p.dominio+'","'+addr[0]+':'+str(addr[1])+'"," дал IP от DNS гугла")')
                      con.commit()
          th = Thread(target=work)
          th.start()





      except BaseException:
           ip=''

  except KeyboardInterrupt:
    print 'end'
    udps.close()
    con.close()
