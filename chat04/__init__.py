# -*- coding: utf-8 -*-
# @Time    : 2017/11/17 12:21
# @Author  : Ayan
# @Email   : hbally
# @File    : __init__.py.py
# @Software: PyCharm

"""
引入心跳机制，防止意外断线
1.服务器首先接收心跳包，刷新心跳时间;然后开启任务定时检查心跳时间是否超时，若超时主动断开conn
2.客服端定时发送心跳包，

"""
