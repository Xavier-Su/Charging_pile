import json
import os
import socket


def loadCfg():
    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    cfgFile = os.path.join(CUR_PATH, "ini.cfg")
    global GWIP, GPSPOS
    try:
        f = open(cfgFile)
        t = f.read()
        f.close()
        cfg = json.loads(t)
        GWIP = cfg["gateway"]
        GPSPOS = cfg["gpspos"]
        print('load cfg', GWIP, GPSPOS)
    except:
        GWIP = '127.0.0.1'
        GPSPOS = "114.406319&30.462533"

class zhiyun():
    loadCfg()
    GW_HOST = GWIP
    GW_PORT = 7003

    MASTER_HOST = '192.168.31.100'
    MASTER_PORT = 8080
    MASTER_GPS = GPSPOS
    D1 = ''
    recv_data=''
    slave_addr=''

    zhiyun_gw = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    zhiyun_gw.bind((MASTER_HOST,MASTER_PORT))
    # zhiyun_gw=''
    def __init__(self):
        D1 = ''
        # zhiyun_gw = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def send_web(self,data):
        self.zhiyun_gw.sendto(data,(self.GW_HOST,self.GW_PORT))

    def recv_web(self):

        # while True:
        self.recv_data,self.slave_addr=self.zhiyun_gw.recvfrom(256)
        # print('recv_data, slave_addr')
        # print(self.recv_data,self.slave_addr)


