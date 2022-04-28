import binascii
import threading
import time
import serial


# 端口：CNU； Linux上的/dev /ttyUSB0等； windows上的COM3等
portx = "COM9"
# 波特率，标准值有：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
bps = 9600
# 超时设置，None：永远等待操作；
#         0：立即返回请求结果；.02
#        其他：等待超时时间（单位为秒）
timex = 5
# 打开串口，并得到串口对象
ser = serial.Serial(portx, bps, timeout=timex)
# 写数据
# a = '01 10 00 10 00 01 02 55 55 5B AF'
# rtu_all = '0110001000010255555BAF'

def uart_send(rtu_all):
    try:
        # 简单的发送16进制字符
        # ser.write(b'\xFE\xFE\xFE')
        # 但是上面的方法不够优雅，需要自己添加\x，非常麻烦，于是使用下面这个方法
        d = bytes.fromhex(rtu_all)
        print(d)
        # 串口发送数据
        result = ser.write(d)
        # result = ser.write(chr(0x10).encode("utf-8"))
        # result = ser.write("02040000000271F8".encode("gbk"))
        print("写总字节数：", result)
        # 数据的接收
        # ser.close()  # 关闭串口
    except Exception as e:
        print("error!", e)

def uart_recv():
    while True:
        time.sleep(0.2)
        count = ser.inWaiting()
        if count > 0:
            data = ser.read(count)
            if data != b'':
                # 将接受的16进制数据格式如b'h\x12\x90xV5\x12h\x91\n4737E\xc3\xab\x89hE\xe0\x16'
                #                      转换成b'6812907856351268910a3437333745c3ab896845e016'
                #                      通过[]去除前后的b'',得到我们真正想要的数据
                recv_data=str(binascii.b2a_hex(data))[2:-1]
                print("receive:",recv_data)
                return recv_data

if __name__ == '__main__':
    while True:
        sen = threading.Thread(target=uart_send)
        sen.setDaemon(True)
        sen.start()
        rec = threading.Thread(target=uart_recv)
        rec.setDaemon(True)
        rec.start()

        time.sleep(60)