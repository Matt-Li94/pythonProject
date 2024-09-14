import requests, json, threading
from bs4 import BeautifulSoup
import numpy as np
import re
from tqdm import trange
from pymongo import MongoClient as Client
import xlwt

city = ['北京', '上海', '广东', '深圳']
e_city = ['beijing', 'shanghai', 'guangdong', 'shenzheng', 'shenyang', 'dalian']
eshouse = ['https://esf.fang.com/house/i3{}/', 'https://sh.esf.fang.com/house/i3{}/',
           'https://gz.esf.fang.com/house/i3{}/', 'https://sz.esf.fang.com/house/i3{}/']


is_craw = {}
proxies = []
workbook = xlwt.Workbook()
sheet = workbook.add_sheet('sheet1')

def write_to_mongo(ips, city):
    '''将数据写入mongoDB'''
    client = Client(host='localhost', port=27017)
    db = client['fs_db']
    coll = db[city + '_good']

    for ip in ips:
        coll.insert_one({'name': ip[0], \
                         'price': ip[1],
                         'addresses': ip[2],
                         'areas': ip[3],
                         'eq': ip[4]})
    client.close()


def read_from_mongo(city):
    client = Client(host='localhost', port=27017)
    db = client['fs_db']
    coll = db[city + '_good']
    li = coll.find()
    client.close()
    return li


class Consumer(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self, args=args)

    def run(self):

        global is_craw
        url_demo, i, city_id, lock = self._args
        print("{}, 第{}页".format(city[city_id], i))
        url = url_demo.format(i)

        soup = get_real(url)

        names = []
        for name in soup.select('.tit_shop'):
            names.append(name.text.strip())

        addresses = []
        for item in soup.find_all('p', attrs={'class': 'add_shop'}):
            address = item.a.text + " " + item.span.text
            addresses.append(address.replace('\t', '').replace('\n', ''))

        es = []
        for item in soup.find_all('p', attrs={'class': 'tel_shop'}):
            es.append(item.text.replace('\t', '').replace('\n', ''))

        moneys = []
        for money in soup.find_all("span", attrs={"class": 'red'}):
            moneys.append(money.text.strip())

        areas = []
        for area in soup.find_all('dd', attrs={'class': 'price_right'}):
            areas.append(area.find_all('span')[-1].text)

        houses = []
        for idx in range(len(names)):
            try:
                item = [names[idx], moneys[idx], addresses[idx], areas[idx], es[idx]]
                print(item)
                #sheet.write(item)  # row, column, value
                houses.append(item)
            except Exception as e:
                print(e)
                #sheet.write(item)  # row, column, value

        lock.acquire()
        write_to_mongo(houses, e_city[city_id])
        lock.release()

        print("线程结束{}".format(i))



def dict2proxy(dic):
    s = dic['type'] + '://' + dic['ip'] + ':' + str(dic['port'])
    return {'http': s, 'https': s}


def get_real(url):
    resp = requests.get(url, headers=header)
    soup = BeautifulSoup(resp.content, 'html.parser', from_encoding='gb18030')
    if soup.find('title').text.strip() == '跳转...':

        pattern1 = re.compile(r"var t4='(.*?)';")
        script = soup.find("script", text=pattern1)
        t4 = pattern1.search(str(script)).group(1)

        pattern1 = re.compile(r"var t3='(.*?)';")
        script = soup.find("script", text=pattern1)
        t3 = re.findall(pattern1, str(script))[-1]
        url = t4 + '?' + t3
        HTML = requests.get(url, headers=header)
        soup = BeautifulSoup(HTML.content, 'html.parser', from_encoding='gb18030')
    elif soup.find('title').text.strip() == '访问验证-房天下':
        pass

    return soup


def read_proxies():
    client = Client(host='localhost', port=27017)
    db = client['proxies_db']
    coll = db['proxies']
    # 先检测，再写入，防止重复
    dic = list(coll.find())
    client.close()
    return dic


def craw():
    lock = threading.Lock()

    for idx in trange(len(e_city)):

        url = eshouse[idx]
        soup = get_real(url.format(2))
        try:
            page_number = int(soup.find('div', attrs={'class': 'page_al'}).find_all('span')[-1].text[1:-1])
            pages = list(range(1, page_number + 1))
        except:
            pages = list(range(1, 101))
        url_demo = url

        ts = []
        # pages = [1, 2, 3]
        while len(pages) != 0:
            for i in range(10):
                t = Consumer((url_demo, pages.pop(), idx, lock))
                t.start()
                ts.append(t)

                if len(pages) == 0:
                    break

            for t in ts:
                t.join()
                ts.remove(t)

if __name__ == '__main__':

    craw()

