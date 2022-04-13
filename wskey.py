import os
import random
import time

from gevent import monkey

monkey.patch_all()
from requests.adapters import HTTPAdapter, Retry
import json
import gevent
import requests
from gevent.queue import Queue
from requests.exceptions import ProxyError, ConnectionError
from urllib3.exceptions import MaxRetryError

PROXY_URL = "123456"

requests.packages.urllib3.disable_warnings()

wsck_lists = []


def getToken(wskey, proxies):
    # proxy = get_proxy()
    # # proxies = {
    # #     "http": "http://" + proxy,
    # #     "https": "https://" + proxy
    # # }
    # proxies = {
    #     "http": "socks5://" + proxy,
    #     "https": "socks5://" + proxy
    # }
    try:
        url = "http://43.135.90.23/" + 'check_api'
        headers = {"authorization": "Bearer Shizuku"}
        res = requests.get(url=url, verify=False, headers=headers, timeout=20).text
        c_info = json.loads(res)
        ua = c_info["User-Agent"]
    except:
        # print("")
        return
    try:
        url = "http://43.135.90.23/" + 'genToken'
        header = {"User-Agent": ua}
        params = requests.get(url=url, headers=header, verify=False, timeout=20).json()
    except Exception as err:
        print("Params参数获取失败")
        print(str(err))
        return
    headers = {
        'cookie': wskey,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'charset': 'UTF-8',
        'accept-encoding': 'br,gzip,deflate',
        'user-agent': ua
    }
    url = 'https://api.m.jd.com/client.action'
    data = 'body=%7B%22to%22%3A%22https%253a%252f%252fplogin.m.jd.com%252fjd-mlogin%252fstatic%252fhtml%252fappjmp_blank.html%22%7D&'
    try:
        sess = requests.session()
        sess.keep_alive = False
        sess.mount("https://", HTTPAdapter(max_retries=Retry(total=1)))
        res = sess.post(url=url, params=params, headers=headers, data=data, proxies=proxies, verify=False,
                            timeout=3)
        res_json = json.loads(res.text)
        tokenKey = res_json['tokenKey']
    except MaxRetryError:
        print("更换ip")
        return False
    #     getToken(wskey)
    except ProxyError:
        print("更换ip")
        return False
    #     getToken(wskey)
    except ConnectionError:
        print("更换ip")
        return False
    #     getToken(wskey)
    except requests.exceptions.RequestException as e:
        print("更换ip")
        return False
    #     getToken(wskey)
    except Exception as err:
        print("JD_WSKEY接口抛出错误 尝试重试 更换IP")
        print(str(err))
        return False
    else:
        return appjmp(wskey, tokenKey, ua, proxies)


# 返回值 bool jd_ck
def appjmp(old_wskey, tokenKey, ua, proxies):
    wskey = "pt_" + str(old_wskey.split(";")[0])
    if tokenKey == 'xxx':
        print(str(wskey) + ";WsKey状态失效\n--------------------\n")
        return False, wskey
    headers = {
        'User-Agent': ua,
        'accept': 'accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'x-requested-with': 'com.jingdong.app.mall'
    }
    params = {
        'tokenKey': tokenKey,
        'to': 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html',
    }
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'
    try:
        sess = requests.session()
        sess.keep_alive = False
        sess.mount("https://", HTTPAdapter(max_retries=Retry(total=1)))
        res = sess.get(url=url, headers=headers, params=params, proxies=proxies, verify=False,
                           allow_redirects=False,
                           timeout=1.5)
    except MaxRetryError:
        print("更换ip")
        return False
        # getToken(wskey)
    except ProxyError:
        print("更换ip")
        return False
        # getToken(wskey)
    except ConnectionError:
        print("更换ip")
        return False
        # getToken(wskey)
    except requests.exceptions.RequestException as e:
        print("更换ip")
        return False
        # getToken(wskey)
    except Exception as err:
        print("JD_appjmp 接口错误 请重试或者更换IP\n")
        print(str(err))
        return False
    else:
        try:
            res_set = res.cookies.get_dict()
            pt_key = 'pt_key=' + res_set['pt_key']
            pt_pin = 'pt_pin=' + res_set['pt_pin']
            # jd_ck = str(pt_key) + '; ' + str(pt_pin) + '; __time=' + str(time.time())
            jd_ck = str(pt_key) + ';' + str(pt_pin) + ";"
            print(jd_ck)
        except Exception as err:
            print("JD_appjmp提取Cookie错误 请重试或者更换IP")
            print(str(err))
            return False
        else:
            if 'fake' in pt_key:
                print(str(wskey) + ";WsKey状态失效")
            else:
                write_ck(jd_ck + "\n")
                wsck_lists.append(old_wskey)
                print(str(wskey) + ";WsKey状态正常")


wsck_queue = Queue()


def get_proxy():
    url = PROXY_URL
    res = requests.get(url)
    if "DB1" in res.text:
        print(res.text)
        exit()
    return res.text


class Proxy:
    def __init__(self):
        self.proxies = {
            "http": "http://",
            "https": "https://"
        }

    def change(self):
        proxy = get_proxy()
        # proxy = "101.42.108.25:5815"
        self.proxies.update(
            {
                "http": f"socks5://{proxy}",
                "https": f"socks5://{proxy}"
            }
        )


def crawler():
    time.sleep(random.randint(100, 500)/100)
    proxy = Proxy()
    proxy.change()
    while not wsck_queue.empty():
        wsck = wsck_queue.get_nowait()
        if not getToken(wsck, proxies=proxy.proxies):
            proxy.change()
            getToken(wsck, proxies=proxy.proxies)
        print("还有：", wsck_queue.qsize(), "个wsck未转换")


def read_wsck():
    with open("1.txt", "r") as f:
        wsck = f.read()
    return wsck.split("\n")


def write_ck(ck):
    with open("./jdCookie.txt", "a+", encoding="utf-8")as f:
        f.write(ck)


def init():
    if os.path.exists("./jdCookie.txt"):
        os.remove("./jdCookie.txt")
    with open("./jdCookie.txt", "w", encoding="utf-8")as f:
        f.write("")


def main():
    init()
    wsck_list = read_wsck()
    random.shuffle(wsck_list)
    for wsck in wsck_list:
        wsck_queue.put_nowait(wsck)
    tasks_list = []
    for x in range(200):
        task = gevent.spawn(crawler)
        tasks_list.append(task)
    gevent.joinall(tasks_list)
    with open("new_jdwc.txt", "w")as f:
        f.write("\n".join(wsck_lists))


if __name__ == '__main__':
    main()
