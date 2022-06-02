from ctypes.wintypes import SIZEL
import hashlib
from math import ceil,log,floor
from opcode import hasjabs
import sys
import socket
import time
def compute_checksum(packet):
    return hashlib.md5(packet.encode("utf-8")).hexdigest()
def senddata(path,ip_receiver,port_receiver, port_sender, uid,size=-1):
    #port initialization
    tout=10
    addedmsg=""
    client= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(("",port_sender))
    #codes here
    #stage1-> transaction ID
    msg="ID"+uid
    datafile=open(path,"r")
    data=datafile.readline()
    datafile.close()
    client.sendto(msg.encode(), (ip_receiver,port_receiver))
    transid, addr = client.recvfrom(4096)
    wrongchecksum=False
    counter=0
    timouts=0
    tid=transid.decode()
    exectime=time.perf_counter()
    partdata=data[0]
    msg=f"ID{uid}SN{counter:07d}TXN{tid}LAST0{partdata}"
    #print(msg)
    addedmsg+=partdata
    hashdata=compute_checksum(msg)
    sendtime=time.perf_counter()
    client.sendto(msg.encode(), (ip_receiver,port_receiver))
    rdata, addr = client.recvfrom(1024)
    #print((rdata.decode())[23:],hashdata)
    cs=rdata.decode()#23 is the number of chars frm ACK to 5 of md5
    if cs[23:]!=hashdata:
        print("wrong checksum")
        wrongchecksum=True
        print(cs[23:],hashdata)
        return
    ptime=(time.perf_counter()-sendtime)
    print(ptime)
    client.settimeout(ptime+2)
    size=ceil(len(data)/((120/ceil(ptime))))
    size=size-1+ceil(size/(size-1)) #distribute the last packet
    usize=size-ceil(size/10)
    print(size)
    counter+=1
    i=1
    maxfound=False
    while i<=len(data):
        remaining=len(data)//size+bool(len(data)%size)
        print("sending packet:",(counter),"/",len(div))
        partdata=data[i:i+size]
        a=int(not ((i+size)<len(data)))
        msg=f"ID{uid}SN{counter:07d}TXN{tid}LAST{a}{partdata}"
        #print(msg)
        hashdata=compute_checksum(msg)
        sent=False
        while not sent:
            try:
                sendtime=time.perf_counter()
                client.sendto(msg.encode(), (ip_receiver,port_receiver))
                rdata, addr = client.recvfrom(1024)
                #print((rdata.decode())[23:],hashdata)
                ptime=time.perf_counter()-sendtime
                #print(ptime)
                cs=rdata.decode()#23 is the number of chars frm ACK to 5 of md5
                #print("the same hash:",(rdata.decode())[23:]==hashdata)
                if cs[23:]!=hashdata:
                    wrongchecksum=True
                    break
                counter+=1
                sent=True
                addedmsg+=partdata
                i+=size
                if not maxfound:
                    temp=(usize+size)//2
                    if temp==size:
                        maxfound=True
                    usize=size-(size//10)
            except TimeoutError:
                #print("timeout-resending data...")
                if counter==1:
                    temp=(usize+size)//2
                    if temp==size:
                        maxfound=True
                if time.perf_counter()-exectime>121:
                    print("overtime")
                    break
                pass
        if time.perf_counter()-exectime>121:
            break
    print("time taken:",time.perf_counter()-exectime)
    print("data and sent data are the same:",data==addedmsg)
    print("transaction id:",tid)
    if wrongchecksum:# wrong data sent , need to resend whole data
        print("wrong checksum")
if __name__=="__main__":
    arguments=sys.argv
    #setting default values
    ipr='10.0.7.141'
    portr=9000
    ports=6756
    uid="9bb836ec"
    payload="9bb836ec.txt"
    #assuming python file always goes first
    for i in range(0,len(arguments[1:]),2):
        if arguments[i+1]=="-f":
            payload=arguments[i+2]
        elif arguments[i+1]=="-a":
            ipr=arguments[i+2]
        elif arguments[i+1]=="-s":
            portr=int(arguments[i+2])
        elif arguments[i+1]=="-c":
            ports=int(arguments[i+2])
        elif arguments[i+1]=="-i":
            uid=arguments[i+2]
    senddata(payload,ipr,portr,ports,uid)
