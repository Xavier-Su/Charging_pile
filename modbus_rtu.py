# !/usr/bin/python3
import string
import time

import define
import binascii
import uart
import struct


class Modbus_Rtu:
    Rtu_data = ''             #还未加crc校验值的指令
    Rtu_all=''                #已加crc校验值的指令
    addr=''                   #从机地址
    function_code=00          #功能码
    reg=''                    #寄存器地址
    length=''                 #读取数据长度
    data=''                   #写入电表的数据
    crc=0xFFFF                #crc校验值
    recv_data=''              #从串口接收回来的值
    float=0.0                 #电表返回的16进制数据转浮点型的数值

    def Assemble_rtu_read(self,addr,function_code,reg,length):              #组装读电表数据的RTU帧
        self.addr=addr
        self.function_code=function_code
        self.reg=reg
        self.length=length

        if self.function_code == define.READ_REGISTERS:             #判断是否为读电表数据

            Rtu_data = self.addr+self.function_code+self.reg+self.length
            self.crc = Rtu.CRC_generate(Rtu_data)
            self.Rtu_all=self.addr+self.function_code+self.reg+self.length+self.crc
            print(self.Rtu_all)
            uart.uart_send(self.Rtu_all)
            time.sleep(0.1)
            return 1

    def Assemble_rtu_write(self,addr,function_code,reg,length,data):              #组装写电表数据的RTU帧
        self.addr=addr
        self.function_code=function_code
        self.reg=reg
        self.length=length
        self.data=data

        if self.function_code == define.WRITE_REGISTERS:             #判断是否为写电表数据

            self.Rtu_data = self.addr + self.function_code + self.reg + self.length+self.data
            self.crc = Rtu.CRC_generate(self.Rtu_data)
            self.Rtu_all = self.Rtu_data + self.crc
            print(self.Rtu_all)
            uart.uart_send(self.Rtu_all)
            time.sleep(0.5)
            return 1



    def Analysis_rtu(self, recv_data):               #解析RTU帧
        self.recv_data = recv_data
        self.function_code = self.recv_data[2:4]               #提取RTU帧中的功能码
        if self.function_code == define.READ_REGISTERS:         #判断功能码类别为读
            print("function read")
            if self.CRC_checkout(self.recv_data[0:14]) != 1:          #将除去crc校验位的部分拿去重新生成crc校验位
                print("crc error!")
                return 0                              #原crc校验位与重新生成crc校验位不符合，数据错误，丢弃
            print("crc ok!")
            self.addr = self.recv_data[0:2]
            print("从机地址"+self.addr)

            print("功能码" + self.function_code)
            self.length = self.recv_data[4:6]
            print("数据长度"+self.length)
            self.data = self.recv_data[6:14]
            float = struct.unpack('!f', bytes.fromhex(self.data))[0]            #16进制数据转浮点型数据
            print("数据内容",float)

            self.crc = self.recv_data[14:18]
            print("CRC校验"+self.crc)
            return 1

        if self.function_code == define.WRITE_REGISTERS:         #判断功能码类别为读
            print("function write")
            if self.CRC_checkout(self.recv_data[0:12]) != 1:    #将除去crc校验位的部分拿去重新生成crc校验位
                print("crc error!")
                return 0  # 原crc校验位与重新生成crc校验位不符合，数据错误，丢弃
            print("crc ok!")
            self.addr = self.recv_data[0:2]
            print("从机地址" + self.addr)

            print("功能码" + self.function_code)
            self.reg = self.recv_data[4:8]
            print("寄存器地址" + self.reg)
            self.length = self.recv_data[8:12]
            print("数据长度", self.length)

            self.crc = self.recv_data[12:16]
            print("CRC校验" + self.crc)
            return 1

    def CRC_checkout(self,recv_data):
        self.Rtu_data=self.CRC_generate(recv_data)       #拿回crc生成值
        print(self.Rtu_data)
        if self.function_code == define.READ_REGISTERS:
            self.crc = self.recv_data[14:18]                #获得接收文本中的crc校验位
            # print(self.Rtu_data)
            # print(self.crc)
            if self.Rtu_data == self.crc:               #对比重新生成的crc校验值和原来的校验值，相同返回1
                return 1

        if self.function_code == define.WRITE_REGISTERS:
            self.crc = self.recv_data[12:16]                #获得接收文本中的crc校验位
            # print(self.Rtu_data)
            # print(self.crc)
            if self.Rtu_data == self.crc:               #对比重新生成的crc校验值和原来的校验值，相同返回1
                return 1


    def CRC_generate(self,string):             #生成CRC校验位
        # string='011000100001'
        # print(string)
        data = bytearray.fromhex(string)
        # print("data ",data)
        self.crc = 0xFFFF
        for pos in data:
            self.crc ^= pos
            for i in range(8):
                if ((self.crc & 1) != 0):
                    self.crc >>= 1
                    self.crc ^= 0xA001
                else:
                    self.crc >>= 1
        str_crc=hex(((self.crc & 0xff) << 8) + (self.crc >> 8))
        # print(str_crc)
        return str_crc[2:6].zfill(4)     #（[2:6]的意思是丢弃0x字符，只拿校验位数据） 一些结果以0开头，会自动把0给吞掉 .zfill(4)可以让结果以4位二进制的形式出现




if __name__ == '__main__':
    Rtu = Modbus_Rtu()
    # 读取1表的电压
    Rtu.Assemble_rtu_read(define.ADDR01,define.READ_REGISTERS,define.voltage,define.voltage_length)
    # 读取2表的电流
    Rtu.Assemble_rtu_read(define.ADDR01, define.READ_REGISTERS, define.current, define.current_length)
    # 读取1表的总有功电量
    Rtu.Assemble_rtu_read(define.ADDR01, define.READ_REGISTERS, define.always_active_power, define.read_length)
    # 写1表电源打开
    Rtu.Assemble_rtu_write(define.ADDR01, define.WRITE_REGISTERS, define.Power_operation,define.write_length_power, define.power_on)
    # 写1表电源关闭
    Rtu.Assemble_rtu_write(define.ADDR02, define.WRITE_REGISTERS, define.Power_operation,define.write_length_power, define.power_off)
    # 接收串口数据进行解析RTU帧
    Rtu.Analysis_rtu(uart.uart_recv())
