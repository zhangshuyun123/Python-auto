#-*- coding：utf-8 -*-

import socket
import pymysql
import hashlib
import hmac
import base64
import time
from urllib import parse
import urllib.request
import requests
from urllib.parse import urlencode
import json

daily_debug_list = []
pre_debug_list = []
online_debug_list = []
def connect_socket(host, port, listname, app_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    if result == 0:
        # print("Port is open")
        listname.append(app_name)
    else:
        pass
        # print("Port is not open")


def select_debug():
    connect = pymysql.connect(host='172.20.47.57', port=3357, user='ro_all_db', password='9s81SI.#X0',
                              database='yonyou_cloud')
    # print("mysql connect successful")
    cur = connect.cursor()
    daily_debug_sql = "select m.app_name, m.app_id from app_manage m, app_service_debug d where m.app_id = d.app_id and d.dr = 0 and m.dr = 0 and m.parent like '/13569/%' and m.app_type='daily'"
    cur.execute(daily_debug_sql)
    daily_res = eval(str(cur.fetchall()))
    for i in range(len(daily_res)):
        app_id = daily_res[i][1]
        app_name = daily_res[i][0]
        # print(app_id)
        host_sql = "select external_ips,port from app_service_debug where app_id='" + "%s"%app_id + "'"
        cur.execute(host_sql)
        debug_res = eval(str(cur.fetchall()))
        id_host = debug_res[0][0]
        id_port = debug_res[0][1]
        #print(id_host, id_port)

        connect_socket(id_host, id_port, daily_debug_list, app_name)
    print("日常 debug 应用为：", daily_debug_list)

    pre_debug_sql = "select m.app_name, m.app_id from app_manage m, app_service_debug d where m.app_id = d.app_id and d.dr = 0 and m.dr = 0 and m.parent like '/13569/%' and m.app_type='pre'"
    cur.execute(pre_debug_sql)
    pre_res = eval(str(cur.fetchall()))
    for i in range(len(pre_res)):
        pre_app_id = pre_res[i][1]
        pre_app_name = pre_res[i][0]
        # print(app_id)
        host_sql = "select external_ips,port from app_service_debug where app_id='" + "%s" % pre_app_id + "'"
        cur.execute(host_sql)
        pre_debug_res = eval(str(cur.fetchall()))
        pre_id_host = pre_debug_res[0][0]
        pre_id_port = pre_debug_res[0][1]
     #   print(pre_id_host, pre_id_port)
        connect_socket(pre_id_host, pre_id_port, pre_debug_list, pre_app_name)
    print("预发 debug 应用为：", pre_debug_list)

    online_debug_sql = "select m.app_name, m.app_id from app_manage m, app_service_debug d where m.app_id = d.app_id and d.dr = 0 and m.dr = 0 and m.parent like '/13569/%' and m.app_type='online'"
    cur.execute(online_debug_sql)
    online_res = eval(str(cur.fetchall()))
    for i in range(len(online_res)):
        online_app_id = online_res[i][1]
        online_app_name = online_res[i][0]
        # print(app_id)
        online_host_sql = "select external_ips,port from app_service_debug where app_id='" + "%s" % online_app_id + "'"
        cur.execute(online_host_sql)
        online_debug_res = eval(str(cur.fetchall()))
        online_id_host = online_debug_res[0][0]
        online_id_port = online_debug_res[0][1]
        #print(online_id_host, online_id_port)
        connect_socket(online_id_host, online_id_port, online_debug_list, online_app_name)
    print("生产 debug 应用为：", online_debug_list)
    cur.close()

def sendmessage():
    # 当前时间戳
    timestamp = int(time.time() * 1000)
    #print("获取当前时间的时间戳", timestamp)
    yonzoneApiAppKey = ""
    yonzoneApiSecret = ""
    message = "appKey" + yonzoneApiAppKey + "timestamp" + str(timestamp)
    paramap = base64.b64encode(
        hmac.new(yonzoneApiSecret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest())
    signature = urllib.parse.quote(paramap)
    access_token_url = 'https://open.yonyoucloud.com/open-auth/selfAppAuth/getAccessToken?appKey=%s&timestamp=%s&signature=%s' % (
    yonzoneApiAppKey, timestamp, signature)
    #print(access_token_url)

    get_accesstoken_res = requests.get(url=access_token_url)
    # print(get_accesstoken_res.status_code)
    # print(get_accesstoken_res.text)

    accesstoken_time = eval(get_accesstoken_res.text)['data']['expire']
    #　print(accesstoken_time)
    accesstoken = eval(get_accesstoken_res.text)['data']['access_token']
    # print(accesstoken)
    # print(daily_debug_list)

    sendmessage = """======Debug检查通知=======
            ===生产环境===
        共有 %s 个应用开启 debug ：
%s
*************************************************
            ===预发环境===
        共有 %s 个应用开启 debug ：
%s
*************************************************
            ===日常环境===
        共有 %s 个应用开启 debug ：
%s
    """%(len(online_debug_list), online_debug_list, len(pre_debug_list), pre_debug_list, len(daily_debug_list), daily_debug_list)
    # print(sendmessage)
    base_url = 'https://api.diwork.com/diwork/uspace/group/message_muc_text?'
    params = {
        'access_token': accesstoken
    }
    data = {
        'yhtUserId': '',
        'content': sendmessage,
        'mucId': ''
    }
    message_url = base_url + urlencode(params)
    send_message_res = requests.post(url=message_url, data=json.JSONEncoder().encode(data))
    print(send_message_res.text)

if __name__ == '__main__':
    select_debug()
    sendmessage()
