import threading
import modbus_rtu
import web_zhiyun
import define
import time
import web_send_recv

Web = web_zhiyun.zhiyun()
lock=1

def Analysis_command(Addr, command_text, command_value,mac):
    D1 = 0
    myMAC=mac
    MAC = Addr + myMAC[2:17]
    if command_text == 'OD1' and command_value == '1':
        ON = modbus_rtu.power_on(Addr)
        print("+++++++++++++++")
        if ON == 'ON':
            D1 = int(command_value)
            report_power_status(MAC, Addr)
            print("power on ok")

    if command_text == 'CD1' and command_value == '0':
        OFF = modbus_rtu.power_off(Addr)
        print("+++++++++++++++")
        if OFF == 'OFF':
            D1 = int(command_value)
            report_power_status(MAC, Addr)
            print("power off ok")


def recv_command(gw,mac):
    myMAC=mac
    global lock
    recv_data, slave_addr = gw.zhiyun_gw.recvfrom(256)
    if lock == 1:
        lock =0
        print('recv data and slave addr ok!')
        # print(recv_data, slave_addr)
        recv_data = recv_data.decode()
        Addr = recv_data[0:2]
        # print(recv_data, Addr)
        try:
            if recv_data[17] == '=' and recv_data[2:17] == myMAC[2:17]:
                recv_data = recv_data[18:]
                # print(recv_data)
                if recv_data[0] == '{' and recv_data[-1] == '}':
                    resp = []
                    order = recv_data[1:-1].split(",")
                    # print(order)
                    for i in order:
                        command = i.split("=")  #
                        if len(command) == 2:
                            command_text = command[0]
                            command_value = command[1]
                            Analysis_command(Addr, command_text, command_value,mac)
                            # print(command_text, command_value)
            lock=1
        except(IndexError):
            print("发现异常！跳过本次循环。")
            pass


def auto_control(Web,mac):
    global lock

    while True:
        gw = Web
        mac = mac
        # string = mac + '={A0=0.00,A1=0.00,A2=00.00,A3=000.22,A4=00.00,A6=0,A7=0}'
        # gw.send_web(string.encode())
        # while True:
        print('---------------------------------------------')
        recv_command(gw,mac)
        # time.sleep(0.1)


def report_power_status(mac, addr):
    status = -1
    if modbus_rtu.power_status(addr) == 'OFF':
        status = 0
    if modbus_rtu.power_status(addr) == 'ON':
        status = 1
    if status != -1:
        msg1 = mac + "=" + "{D1=%d}" % status
        Web.send_web(msg1.encode())
    else:
        print("report power error")


class Master:
    STATUS_DEVICE_OFFLINE = -1
    STATUS_IDLE = 0
    STATUS_CHARGING = 1

    def __init__(self, mac, addr):
        print("==================")
        self.mac = mac
        self.addr = addr
        self.D0 = 0xff  # 主动上报使能
        self.D1 = 0  # 开关控制

        self.A0 = 0.01  # 历史用电量
        self.A1 = 0.20  # 电流
        self.A2 = 180.56  # 电压
        self.A3 = 4022.33  # 功率
        self.A4 = 110.03  # 实时负载充电

        self.A5 = 0  #
        self.A6 = 0  # 充电开始时间
        self.A7 = 0  # 充电结束时间

        self.V0 = 5  # 主动上报时间间隔
        self.V1 = 0  # 储值电量
        # self.V2 = 0
        self.V3 = None  # gps 经度 纬度

        for iter in define.addr_list:
            self.addr = iter
            self.mac = iter + self.mac[2:]
            modbus_rtu.power_on(str(self.addr))
            modbus_rtu.power_off(self.addr)
            report_power_status(self.mac, self.addr)
            self.get_status()
            self.report()


        t = threading.Thread(target=auto_control,args=(Web,myMAC))  # 打开来自网关的接收线程
        t.setDaemon(True)  # 设置守护线程
        t.start()


    def set_addr(self, addr):
        self.addr = addr

    def sendmsg(self, dat):
        msg = self.mac + "=" + dat
        # print(msg)
        Web.send_web(msg.encode())

    def get_status(self):
        if self.STATUS_DEVICE_OFFLINE == modbus_rtu.power_status(self.addr):
            ''' 电表设备不在线，不上报 '''  # !!!!!!!!!! 可能需要向上报问题
            return

        # self.A1 = round(modbus_rtu.read_current(self.addr), 2)  # ！！存在使用过程中会报错的问题
        # self.A2 = round(modbus_rtu.read_voltage(self.addr), 2)
        # self.A3 = round(modbus_rtu.read_Active_power(self.addr), 2)
        # self.A4 = round(modbus_rtu.read_always_active_power(self.addr), 2)

        # print('{:.1f}'.format(3.1415926))
        # print('{:.4f}'.format(3.14))  # .后接保留小数点位数

        try:
            self.A1 = float("%.2f" %(modbus_rtu.read_current(self.addr)))  # ！！存在使用过程中会报错的问题
            self.A2 = float("%.2f" %(modbus_rtu.read_voltage(self.addr)))
            self.A3 = float("%.2f" %(modbus_rtu.read_Active_power(self.addr)))
            self.A4 = float("%.2f" %(modbus_rtu.read_always_active_power(self.addr)))
        except(TypeError):
            pass

    def report(self):
        if self.STATUS_DEVICE_OFFLINE == modbus_rtu.power_status(self.addr):
            ''' 电表设备不在线，不上报 '''  # !!!!!!!!!! 可能需要向上报问题原因
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

    def run(self):
        # self.report()

        lastReportTime = time.time()
        reportD1Time = time.time()
        print("+++++-------+++++")
        try:
            global lock

            while True:
                if lock == 1:
                    lock = 0
                    for iter in define.addr_list:
                        self.addr = iter
                        self.mac = iter + self.mac[2:]
                        self.get_status()
                        self.report()

                # print("before get get_status")
                # if time.time() - lastReportTime > self.V0:
                #     lastReportTime = time.time()
                #     print("after get get get_status")
                #     self.get_status()
                #     self.report()
                # # 检测充电是否结束
                # if (self.D1 & 0x01) and self.STATUS_IDLE == modbus_rtu.power_status(self.addr):
                #     self.D1 &= 0xFE  # 关闭电源
                #     reportD1Time = time.time() - 70  # 强制上报 60一次
                # if time.time() - reportD1Time > 60:
                #     reportD1Time = time.time()
                #     report_power_status(self.mac, self.addr)
                    lock = 1
                    time.sleep(self.V0)

        except(TypeError):
            print("TypeError pass ")
            pass 


if __name__ == '__main__':
    swAddr = '01'
    myMAC = '01:01:20:22:55:4F'
    # mac = None
    # for line in os.popen("ip addr show enp0s3f0"):  # loong edu
    #     if "link/ether" in line:
    #         mac = line.split()[1].upper()
    #         break
    # if mac == None:
    #     for line in os.popen("ifconfig eth0"):  # 9x25
    #         if "HWaddr" in line:
    #             mac = line.split()[4].upper()
    #             break
    # if mac == None:
    #     logging.error("get mac addr!")
    #     sys.exit(0)
    #
    # myMAC = "%02d" % addr
    # myMAC += mac[2:]


    # t1 = threading.Thread(target=Master(myMAC, swAddr).run())  # 打开来自网关的接收线程
    # t1.setDaemon(True)  # 设置守护线程
    # t1.start()

    Master(myMAC, swAddr).run()
    # Master(myMAC, swAddr)
    # while True:
    #     time.sleep(5)
    # master = Master(myMAC, swAddr).run()
    # while True:
    #     if swAddr is 1:
    #         swAddr = 2
    #     elif swAddr is 2:
    #         swAddr = 1
    #
    #     set_addr(swAddr)

