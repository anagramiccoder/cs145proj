import hashlib
import sys
import socket
import time
def compute_checksum(packet):
    return hashlib.md5(packet.encode("utf-8")).hexdigest()
def senddata(path,ip_receiver,port_receiver, port_sender, uid,size=-1):
    #port initialization
    client= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(("",port_sender))
    client.settimeout(5)
    #codes here
    #stage1-> transaction ID
    msg="ID"+uid
    print(msg)
    datafile=open(path,"r")
    data=datafile.readline()
    datafile.close()
    client.sendto(msg.encode(), (ip_receiver,port_receiver))
    transid, addr = client.recvfrom(1024)
    #assume within 90 seconds
    if size==-1:
        size=(len(data)//90)*3
    i=0
    wrongchecksum=False
    counter=0
    while i<len(data):
        partdata=data[i:i+size]
        hashdata=compute_checksum(partdata)
        msg="ID"+uid+transid.decode()+str(counter)+partdata
        print(msg)
        try:
            client.sendto(msg.encode(), (ip_receiver,port_receiver))
            rdata, addr = client.recvfrom(1024)
            cs=rdata.decode()#23 is the number of chars frm ACK to 5 of md5
            print(cs[23:],hashdata)
            if cs[23:]!=hashdata:
                wrongchecksum=True
                break
            counter+=1
            i+=size
        except socket.TimeoutError:
            size=size-1
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
