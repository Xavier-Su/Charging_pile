import time

import web_zhiyun
import modbus_rtu
import web_send_recv
def Analysis_command(Addr,command_text,command_value):
    D1=0
    MAC = '02:01:20:22:55:4F'
    if command_text=='OD1' and command_value=='1':
        ON=modbus_rtu.power_on(Addr)
        D1=int(command_value)
        # NODE=web_send_recv.Node(MAC,Addr)
        web_send_recv.report_power_status(MAC,Addr)
        print("power on ok")

    if command_text=='CD1' and command_value=='0':
        ON=modbus_rtu.power_off(Addr)
        D1=int(command_value)
        # NODE = web_send_recv.Node(MAC, Addr)
        web_send_recv.report_power_status(MAC,Addr)
        print("power off ok")

def recv_command(gw):
    recv_data, slave_addr = gw.zhiyun_gw.recvfrom(256)
    print('recv_data, slave_addr')
    print(recv_data, slave_addr)
    recv_data=recv_data.decode()
    Addr = recv_data[0:2]
    print(recv_data,Addr)
    if recv_data[17] == '=' and recv_data[0:17] == mac:
        recv_data = recv_data[18:]
        print(recv_data)
        if recv_data[0] == '{' and recv_data[-1] == '}':
            resp = []
            order = recv_data[1:-1].split(",")
            print(order)
            for i in order:
                command = i.split("=")  #
                if len(command) == 2:
                    # try:
                        command_text=command[0]
                        command_value = command[1]
                        Analysis_command(Addr,command_text,command_value)
                        print(command_text,command_value)
                    #     ret = __proc(kv[0], kv[1])
                    #     if ret != None:
                    #         resp.append(ret)
                    # except Exception as e:
                    #     traceback.print_exc()
            # if len(resp) > 0:
            #     dat = "{" + ",".join(resp) + "}"
            #     gw.send_web(dat.encode())


if __name__ == '__main__':

    gw = web_zhiyun.zhiyun()

    # gw.recv_web()
    # dat=''
    mac = '01:01:20:22:55:4F'
    while True:
        print('---------------------------------------------')
        string = '02:01:20:22:55:4F={A0=0.02,A1=2.20,A2=60.00,A3=103.22,A4=65.00,A6=0,A7=0}'
        gw.send_web(string.encode())
        recv_command(gw)
        time.sleep(0.1)

