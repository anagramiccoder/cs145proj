import hashlib
from math import ceil,log,floor
from opcode import hasjabs
from sqlite3 import Time
import sys
import socket
import time
def compute_checksum(packet):
    return hashlib.md5(packet.encode("utf-8")).hexdigest()
def senddata(path,ip_receiver,port_receiver, port_sender, uid,size=-1):
    #port initializationaddedmsg=""
    client= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(("",port_sender))
    client.settimeout(30)
    #codes here
    #stage1-> transaction ID
    msg="ID"+uid
    datafile=open(path,"r")
    data=datafile.readline()
    datafile.close()
    client.sendto(msg.encode(), (ip_receiver,port_receiver))
    try:
        transid, addr = client.recvfrom(4096)
    except TimeoutError:
        print("server busy try again later...")
        return
    if(transid.decode()=="Existing alive transaction"):
        print("wait for previous Transaction to finish")
        return
    wrongchecksum=False
    counter=0
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
    client.settimeout(floor(ptime)+2)
    size=floor(len(data)/((100/(ptime+0.2)))) #assumption, all data CAN take less than 95 seconds to process
    size=size+floor(size/((100/ceil(ptime)-1)))# distributing one packet time used by packet 0
    print(size)
    counter+=1
    i=1
    while i<len(data):
        sent=False
        while not sent:
            remaining=len(data)//size+bool(len(data)%size)#compute for possible packets left to be sent
            print("sending packet:",(counter),"/",remaining)
            partdata=data[i:i+size]
            a=int(not ((i+size)<len(data)))
            msg=f"ID{uid}SN{counter:07d}TXN{tid}LAST{a}{partdata}"# packet creation
            #print(msg)
            hashdata=compute_checksum(msg)
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
            except TimeoutError:
                #print("timeout-resending data...")
                if counter==1:
                    if size<170:
                        size=size-ceil(size/8)#9/10 techincally
                    else:
                        size=size//2        #half the datasize, as per trials, no max payload of 150+ or even 100,due to congestions
                    if size<1:
                        size==1
                if time.perf_counter()-exectime>121:
                    print("overtime")
                    break
                pass
        if time.perf_counter()-exectime>121:
            break
    print("time taken:",time.perf_counter()-exectime)
    print("data and sent data are the same and was ACK'ed:",(data==addedmsg and (time.perf_counter()-exectime)<120.5))
    print("transaction id:",tid)
    if wrongchecksum:# wrong data sent , need to resend whole data
        print("wrong checksum")
    client.close()
def testsenddata(path,ip_receiver,port_receiver, port_sender, uid,size=-1):
    print("path:",path,"\nipreceiver:",ip_receiver,"\npoert receiver:",port_receiver, "\nport sender:",port_sender,"\nID:", uid)
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
