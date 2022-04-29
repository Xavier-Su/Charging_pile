import web_zhiyun

if __name__ == '__main__':

    gw = web_zhiyun.zhiyun()
    string ='kkkkk'
        string = '01:01:20:22:55:4F={A0=0.02,A1=2.20,A2=50.00,A3=153.22,A4=65.00,A6=0,A7=0}'

        gw.send_web(string.encode())
    gw.recv_web()
    gw.send_web(string.encode())
