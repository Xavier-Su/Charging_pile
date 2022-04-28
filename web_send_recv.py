# coding=utf-8
import json
import os
import sys

# import thread
import threading
import time
import socket
import traceback

import modbus_rtu


CUR_PATH = os.path.abspath(os.path.dirname(__file__))

cfgFile = os.path.join(CUR_PATH, "ini.cfg")


def loadCfg():
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


class Node:
    STATUS_DEVICE_OFFLINE = -1
    STATUS_IDLE = 0
    STATUS_CHARGING = 1

    # def __init__(self, mac, cp_addr):
    def __init__(self, mac, addr):
        self.mac = mac
        # self.chargingpipe = Chargingpile(cp_addr)

        # self.TYPE = '32509'
        self.D0 = 0xff  # 主动上报使能
        self.D1 = 0  # 开关控制
        self.A0 = 0  # 开关控制
        self.A1 = 2.20  # 电流
        self.A2 = 50.00  #压
        self.A3 = 153.22  # 功率
        self.A4 = 65  # 实时负载充电量

        self.A5 = 0
        self.A6 = 0
        self.A7 = 0

        self.V0 = 30  # 主动上报时间间隔
        self.V1 = 0  # 储值电量
        # self.V2 = 0
        self.V3 = None  # gps 经度 纬度

        # -----------------------------------------
        self.addr = addr  # 选择电表地址

        # self.charging_start_time = 0
        self.charging_start_quantity = 0

        # self.charging_end_time = 0
        self.charging_end_quantity = 0

        # self.charging_limit_time = 0
        self.charging_limit_quantity = 0
        self.status = self.STATUS_CHARGING

        # -----------------------------------------

        self.sim_A0 = 0  # 模拟电量
        self.skgw = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = (GWIP, 7003)

        # t = threading.Thread(target=self.__recv_thread)  # 打开来自网关的接收线程
        # t.setDaemon(True)  # 设置守护线程
        # t.start()

    def get_status(self):
        if self.STATUS_DEVICE_OFFLINE == self.status:
            ''' 电表设备不在线，不上报 '''
            return

        self.A1 = modbus_rtu.read_current(self.addr)
        self.A2 = modbus_rtu.read_voltage(self.addr)
        self.A3 = modbus_rtu.read_voltage(self.addr)
        self.A4 = modbus_rtu.read_always_active_power(self.addr)
        if self.status == self.STATUS_IDLE:  # 充电结束
            self.A4 = self.charging_end_quantity - self.charging_start_quantity
        else:
            self.A4 = self.quantity - self.charging_start_quantity

    #
    # 向网关发送数据 (sendto_cloud)
    #
    def sendmsg(self, dat):
        self.server_addr = (GWIP, 7003)
        msg1 = self.mac + "=" + dat
        msg1 = msg1.encode()
        print(msg1, self.server_addr)
        self.skgw.sendto(msg1, self.server_addr)

    #
    # 询问参数返回对应参数值 ( )
    #
    def __proc(self, tag, val):
        if self.status == self.STATUS_DEVICE_OFFLINE:
            print("设备不在线！！！！")
            return

        if tag == 'ECHO':
            return 'ECHO=%s' % val

        # if tag == 'TYPE':
        #     return 'TYPE=%s' % self.TYPE

        if tag == 'CD0':
            v = int(val)
            self.D0 &= (~v)
        if tag == 'OD0':
            v = int(val)
            self.D0 |= v

        if tag == 'CD1':
            v = int(val)
            if v & 0x01:
                self.chargingpipe.stop_charging()
            self.D1 &= ~v

        if tag == 'OD1':
            v = int(val)
            if v & 0x01:
                self.chargingpipe.start_charging(limit_quantity=self.V1)
            self.D1 |= v

        if tag == 'V0' and val == '?':
            return 'V0=%d' % self.V0
        if tag == 'V0' and val != '?':
            self.V0 = int(val)

        if tag == 'V1' and val == '?':
            return "V1=%.2f" % self.V1
        if tag == 'V1' and val != '?':
            self.V1 = float(val)

        if tag == 'V3':
            if val == '?':
                v3 = GPSPOS
                if self.V3 != None:
                    v3 = self.V3
                return "V3=%s" % v3
            else:
                self.V3 = val

        if tag == 'D0' and val == '?':
            return "D0=%d" % self.D0
        if tag == 'D1' and val == '?':
            return "D1=%d" % self.D1
        if tag == 'A1' and val == '?':
            return "A1=%.2f" % self.A1
        if tag == 'A2' and val == '?':
            return "A2=%.2f" % self.A2
        if tag == 'A3' and val == '?':
            return "A3=%.2f" % self.A3
        if tag == 'A4' and val == '?':
            return "A4=%.2f" % self.A4

    #
    # 收到云端指令 然后执行到__proc返回对应值 并打包上到云端 (recv_switch)
    #
    def __recv_thread(self):
        while True:
            dat, svaddr = self.skgw.recvfrom(256)
            if dat[17] == '=' and dat[0:17] == self.mac:
                dat = dat[18:]
                if dat[0] == '{' and dat[-1] == '}':
                    resp = []
                    its = dat[1:-1].split(",")
                    for it in its:
                        kv = it.split("=")  # 询问值 kv {A0 = ?}
                        if len(kv) == 2:
                            try:
                                ret = self.__proc(kv[0], kv[1])
                                if ret != None:
                                    resp.append(ret)
                            except Exception as e:
                                traceback.print_exc()
                    if len(resp) > 0:
                        dat = "{" + ",".join(resp) + "}"
                        self.sendmsg(dat)

    #
    # 获取并上报当前全部参数 (report_status)
    #
    def report(self):
        if self.STATUS_DEVICE_OFFLINE == self.status:
            ''' 电表设备不在线，不上报 '''
            return

        rep = []
        rep.append("A0=%.2f" % self.A0)
        rep.append("A1=%.2f" % self.A1)
        rep.append("A2=%.2f" % self.A2)
        rep.append("A3=%.2f" % self.A3)
        rep.append("A4=%.2f" % self.A4)
        rep.append("A6=%.0f" % self.A6)
        rep.append("A7=%.0f" % self.A7)

        if len(rep) > 0:
            dat = "{" + ",".join(rep) + "}"
            self.sendmsg(dat)

    #
    # 上报当前开关状态 (report_switch)
    #
    def reportD1(self):
        if self.status != self.STATUS_DEVICE_OFFLINE:
            self.sendmsg("{D1=%d}" % self.D1)

    #
    # 初次运行程序（循环）
    #
    def run(self):
        self.report()
        lastReportTime = time.time()
        reportD1Time = time.time()
        while True:
            self.report()
            self.get_status()
            if time.time() - lastReportTime > self.V0:
                lastReportTime = time.time()
                self.report()
            # 检测充电是否结束
            if (self.D1 & 0x01) and self.STATUS_IDLE == self.status:
                self.D1 &= 0xFE  # 关闭电源
                reportD1Time = time.time() - 70  # 强制上报 60一次
            if time.time() - reportD1Time > 60:
                reportD1Time = time.time()
                self.reportD1()
            time.sleep(2 )


# ----------------------------------------------


if __name__ == '__main__':
    loadCfg()

    addr = 1
    myMAC = '01:01:20:22:55:4F'
    Node(myMAC, addr).run()
