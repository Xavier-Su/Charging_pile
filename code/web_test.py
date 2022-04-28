import web_zhiyun

if __name__ == '__main__':
    gw = web_zhiyun.zhiyun()
    string ='kkkkk'

    gw.recv_web()
    gw.send_web(string.encode())
