import time

import web_zhiyun
import modbus_rtu
import web_send_recv
def Analysis_command(Addr,command_text,command_value):
    D1=0
    MAC = Addr+mac[2:17]
    if command_text=='OD1' and command_value=='1':
        ON=modbus_rtu.power_on(Addr)
        print("+++++++++++++++")
        if ON=='ON':
            D1=int(command_value)
            web_send_recv.report_power_status(MAC,Addr)
            print("power on ok")

    if command_text=='CD1' and command_value=='0':
        OFF=modbus_rtu.power_off(Addr)
        print("+++++++++++++++")
        if OFF == 'OFF':
            D1=int(command_value)
            web_send_recv.report_power_status(MAC,Addr)
            print("power off ok")

def recv_command(gw):

    recv_data, slave_addr = gw.zhiyun_gw.recvfrom(256)
    print('recv_data, slave_addr')
    print(recv_data, slave_addr)
    recv_data=recv_data.decode()
    Addr = recv_data[0:2]
    print(recv_data,Addr)
    try:
        if recv_data[17] == '=' and recv_data[2:17] == mac[2:17]:
            recv_data = recv_data[18:]
            print(recv_data)
            if recv_data[0] == '{' and recv_data[-1] == '}':
                resp = []
                order = recv_data[1:-1].split(",")
                print(order)
                for i in order:
                    command = i.split("=")  #
                    if len(command) == 2:
                        command_text=command[0]
                        command_value = command[1]
                        Analysis_command(Addr,command_text,command_value)
                        print(command_text,command_value)
    except(IndexError):
        print("发现异常！跳过本次循环。")
        pass

def auto_control(mac):
    gw = web_zhiyun.zhiyun()
    mac =mac
    string = mac + '={A0=0.00,A1=0.00,A2=00.00,A3=000.22,A4=00.00,A6=0,A7=0}'
    gw.send_web(string.encode())
    while True:
        print('---------------------------------------------')
        recv_command(gw)
        # time.sleep(0.1)

if __name__ == '__main__':

    # gw.recv_web()
    # dat=''
    mac = '01:01:20:22:55:4F'
    auto_control(mac)

