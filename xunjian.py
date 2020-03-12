# -*- coding:utf-8 -*-

import urllib.error
import socket
import urllib.request
from urllib import parse,request
# 使用文档解析类库
from bs4 import BeautifulSoup
import random
import time

global response
url = 'http://172.20.52.54:11311/oom/yonyou/daily-check/'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/'
              'signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'tenant_name=yonyou; region=online',
    'If-Modified-Since': 'Wed, 05 Feb 2020 02:54:46 GMT',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/79.0.3945.130 Safari/537.36'
}

try:
    response = urllib.request.urlopen('http://172.20.52.54:11311/oom/yonyou/daily-checklist/?uri=bpaas', timeout=5)
except urllib.error.URLError as e:
    if isinstance(e.reason, socket.timeout):
        print("连接超时")

# 读取网页内容
html = response.read().decode('utf-8')

# 解析成文档对象
soup = BeautifulSoup(html, 'html.parser')

# 非法URL 1
invalidLink1 = '#'
# 非法URL 2
invalidLink2 = 'javascript:void(0)'
# 列表、集合
result = []
jihe = set()
# 计数器
mycount = 0
#查找文档中所有a标签
for k in soup.find_all('a'):
    #print(k)
    #查找href标签
    link = k.get('href')
    # 过滤没找到的
    if(link is not None):
          #过滤非法链接
          if link == invalidLink1:
            pass
          elif link == invalidLink2:
            pass
          elif link.find("javascript:")!= -1:
            pass
          else:
            mycount = mycount+1
            jihe.add(link)
            result.append(link[-36:])
print("打印超链接个数:", mycount)
print("打印超链接列表", jihe)

wait_time = random.randint(30, 60)
print("提交表单需等待 %d 秒" %(wait_time))
time.sleep(wait_time)

for i in range(0, len(result)):
    # print(result[i])
    dict = {
        'uuid': result[i],
        'domain': '平台',
        'checker': '方亚利'
    }
    data = bytes(parse.urlencode(dict), encoding='utf-8')
    req = request.Request(url=url, data=data, headers=headers, method='POST')
    response = request.urlopen(req)
    print(response.read().decode('utf-8'))

print("完成")