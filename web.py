# import thread
import threading
import time
import logging
import socket


GWIP = '192.168.20.11'
# GWIP = '192.168.20.132'
# GWIP = '192.168.170.128'
# GWIP = '192.168.137.1'
# mac = '01:01:20:22:44:7b'
# mac= '00:12:4B:00:25:45:70:55'
# mac = '01:01:20:22:55:4F'
mac = '01:01:20:21:02:59'
chargingpipe = 1
TYPE = '32509'
D0 = 0xff
D1 = 1
A0 = 0
A1 = 0.8
A2 = 121.32
A3 = 40
A4 = 20
A5 = 0
A6 = 0
A7 = 0
V0 = 30
V1 = 50
# V2 = 0
V3 = "103.893038&30.792931"


#GWIP = '127.0.0.1'

sim_A0 = 0
# port = 8000
port = 7003
port1 = 7003
skgw = socket.socket(socket.AF_INET ,socket.SOCK_DGRAM)
#server_addr = (GWIP, 7003)
server_addr = (GWIP, port)
server_addr1 = ("", port1)
server_addr2 = (GWIP, port1)

def recv_thread():
    # skgw.bind(server_addr1)
    skgw.connect(server_addr)

    while True:
        #print "000000"
        date1, svaddr = skgw.recvfrom(1024)


        print ("------------")
        print (svaddr)

        if date1[17] == '=' and date1[0:17] == mac:
            date1 = date1[18:]
            print (date1)
        #     LOGGER.debug("%s <<< %s", mac, dat)
        #     if dat[0] == '{' and dat[-1] == '}':
        #         resp = []
        #         its = dat[1:-1].split(",")
        #         for it in its:
        #             kv = it.split("=")
        #             if len(kv) == 2:
        #                 try:
        #                     ret = __proc(kv[0], kv[1])
        #                     if ret != None:
        #                         resp.append(ret)
        #                 except Exception, e:
        #                     traceback.print_exc()
        #         if len(resp) > 0:
        #             dat = "{"+",".join(resp)+"}"
        #             sendmsg(dat)


# thread = threading.Thread(target = recv_thread)


def sendmsg(dat):
    # server_addr = (GWIP, port)
    skgw.sendto((mac +"=" + dat).encode(), server_addr)
    print (mac +"=" + dat, server_addr)




def send():
    while True:
        rep = []
        rep.append("A0=%.2f" % A0)
        rep.append("A1=%.2f" % A1)
        rep.append("A2=%.2f" % A2)
        rep.append("A3=%.2f" % A3)
        rep.append("A4=%.2f" % A4)
        rep.append("A6=%.0f" % A6)
        rep.append("A7=%.0f" % A7)

        # rep.append("A0=%.2f" % A0)
        # rep.append("A1=%.2f" % A1)
        # rep.append("A2=%.2f" % A2)
        # rep.append("A3=%.2f" % A3)
        # rep.append("A4=%.0f" % A4)
        # rep.append("A7=%.0f" % A7)
        # rep.append("D1=%.0f" % D1)
        # rep.append("V1=%.0f" % V1)

        if len(rep) > 0:
            dat = "{" + ",".join(rep) + "}"
            sendmsg(dat)
            print ("ok")
        sendmsg("{D1=%d}" % D1)
        time.sleep(1)

if __name__ == '__main__':

    # thread.start_new_thread(send, ())
    while True:

        sen = threading.Thread(target=send)
        sen.setDaemon(True)
        sen.start()
        #
        t = threading.Thread(target=recv_thread)
        t.setDaemon(True)
        t.start()

        time.sleep(60)


