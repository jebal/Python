# -*- coding:utf-8 -*-

import ConfigParser
import os


if __name__ == '__main__':
    cf = ConfigParser.ConfigParser()
    cf.read("app.conf")

    sender = cf.get("mail", "sender", "jebal")
    receivers = cf.get("mail", "receivers", "kindle")

    recv_list = []
    [recv_list.append(str_recv) for str_recv in receivers]

    print sender, receivers, recv_list
    
