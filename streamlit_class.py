import json
import random
import streamlit as st
from newspaper import Article
from urllib import parse
import urllib
from bs4 import BeautifulSoup
import pdfplumber
import threading
import queue
from lxml import etree
import requests
import hashlib
import time
import re
import pandas as pd


def _md5(parse_txt):
    parse_md5 = hashlib.md5()  # 创建md5对象
    parse_md5.update(parse_txt.encode('utf-8'))
    return parse_md5.hexdigest()


def create_auth():
    """
    获取Authorization
    :return:
    """
    response = requests.get('http://tool.manmanbuy.com/HistoryLowest.aspx')
    if response.status_code == 200:
        searchRet = re.search(r'id="ticket".+value="(?P<value>.+)"', response.text)
        if not searchRet:
            return None
        ticket = searchRet.group('value')
        return 'BasicAuth ' + ticket[-4:] + ticket[:-4]
    return None


def parse_goods_price(urls):
    """
    获取token
    :param urls:
    :return:
    """
    headers = {
        "Authorization":  create_auth(),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "60014_mmbuser=W1cNAAAFDjoAWQUCAFADVQJaW14CA1IFCgJVCVZaVQVXB1MJUwUBBw%3d%3d; acw_tc=784e2cb117046815892607432e226f6d85397e74d3c122d5ab15952ea0ba72; ASP.NET_SessionId=ktjgqaoxdtnf52bmtasxmcmu; Hm_lvt_01a310dc95b71311522403c3237671ae=1702361308,1703208860,1703216505,1704681590; Hm_lvt_85f48cee3e51cd48eaba80781b243db3=1703208860,1703216505,1703466285,1704681590; _gid=GA1.2.525619020.1704681592; _gat_gtag_UA_145348783_1=1; _ga=GA1.1.305938721.1702361277; Hm_lpvt_85f48cee3e51cd48eaba80781b243db3=1704681747; _ga_1Y4573NPRY=GS1.1.1704681591.9.1.1704681755.0.0.0; Hm_lpvt_01a310dc95b71311522403c3237671ae=1704681756",        "Host": "tool.manmanbuy.com",
        "Origin": "http://tool.manmanbuy.com",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://tool.manmanbuy.com/HistoryLowest.aspx?url=https%3A%2F%2Fitem.jd.com%2F10080177096677.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43",
        "X-Requested-With": "XMLHttpRequest"
    }
    time_num = int(time.time() * 1000)
    re_urls = urls.replace(':', '%3A').replace('/', '%2F')
    tokens = f'C5C3F201A8E8FC634D37A766A0299218KEY{re_urls}METHODGETHISTORYTRENDT{time_num}C5C3F201A8E8FC634D37A766A0299218'.upper()
    data = {
        'method': 'getHistoryTrend',
        'key': f'{urls}',
        't': time_num,
        'token': _md5(tokens).upper()
    }
    response = requests.post(url='http://tool.manmanbuy.com/api.ashx', headers=headers, data=data)
    if len(response.text) > 100:
        response = response.json()['data']
        time_list = []
        price_list = []
        for t in eval(response['datePrice']):
            strf_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(t[0]/1000)))
            time_list.append(strf_time)
            price_list.append(t[1])

        info_dict = {
            '链接': response['spUrl'],
            '图片': response['spPic'],
            '商品名称': response['spName'],
            '当前价格': response['currentPrice'],
            '涨幅': response['changPriceRemark'],
            '最低价格': response['lowerPrice'],
            '最低价格日期': response['lowerDate'],
            '历史时间段': time_list,
            '历史时间段价格': price_list
        }
        # print(info_dict)
        return info_dict
    else:
        print('被反扒或者cookie过期')
        return None


def job_info(keys, positionId):
    """
    获取当前工作的信息
    :return:
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "referer": "https://www.zhipin.com/salaryxc/p100109.html",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43",
        "x-requested-with": "XMLHttpRequest"
    }
    url = f"https://www.zhipin.com/wapi/zpboss/h5/marketpay/statistics.json?positionId={positionId}&cityId=0"
    response = requests.get(url=url, headers=headers)
    info_dict = {}
    json_info = response.json()['zpData']['salaryByMonth']
    price_list = []
    for info in json_info:
        times = info['year'] + info['month']
        price = info['monthAveSalary']
        price_list.append(int(price))
        st.write(f'日期:{times}---薪资:{price}')
        infos = {times: price}
        info_dict.update(infos)
    max_pricr = max(price_list)
    for new in info_dict.items():
        if new[1] == max_pricr:
            print(f'职位:{keys}---平均薪资最高日期:{new[0]}---平均薪资最高:{new[1]}')
            return f'职位:{keys}---平均薪资最高日期:{new[0]}---平均薪资最高:{new[1]}'


def get_poems(key):
    """
    查询古诗文
    :param key:
    :return:
    """
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"}
    url = "https://so.gushiwen.cn/search.aspx"
    params = {"value": f"{key}", "valuej": f"{key[0]}"}
    try:
        response = requests.get(url=url, headers=headers, params=params)
        html = etree.HTML(response.text)
        title = html.xpath('''//div[@class="sons"][1]//b//text()''')[0].strip()
        author = html.xpath('''//div[@class="sons"][1]//p[@class="source"]//a//img/@alt''')[0].strip()
        dynasty = html.xpath('''//div[@class="sons"][1]//p[@class="source"]//a//text()''')[-1].strip()
        texts = html.xpath('''//div[@class="sons"][1]//div[@class="contson"]//text()''')
        # print(f'标题:{title}') if title else print(f'标题:{key}')
        # print(f'作者:{dynasty}{author}')
        # print('正文:')
        return title, author, dynasty, texts
        # for txt in texts:
        #     print(txt.strip())
    except Exception as e:
        print(f'采集:{key}---失败--->失败原因:{e}')


def gemini_pro(question):
    headers = {
        "Content-Type": "application/json"
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    params = {
        "key": "AIzaSyBv0WgP7Ahn33pmrt_of52jK8eKDnDlaTQ"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{question}"
                    }
                ]
            }
        ]
    }
    data = json.dumps(data, separators=(',', ':'))
    try:
        response = requests.post(url, headers=headers, params=params, data=data)
        info_json = response.json()
        info = info_json["candidates"][0]["content"]["parts"][0]["text"]
        return info
    except Exception as e:
        print(e)



class Worker(threading.Thread):
    def __init__(self, names, queues):
        threading.Thread.__init__(self)
        self.getName = names
        self.queue = queues
        self.start()  # 执行run()

    def run(self):
        while True:
            if self.queue.empty():
                break
            foo = self.queue.get()
            print(f'{self.getName}当前任务链接:{foo}')
            verfy_ip(foo)
            self.queue.task_done()


def re_txt(txt):
    """
    过滤字符串的杂志
    :param txt: 需要过滤的字符串
    :return:
    """
    html_code = '''
    <b>|</b>|<a>|</a>|<li>|</li>|<span|</span>|class=".*?"|href=".*?"|"https:.*?"|"http:.*?"|https:.*? |http:.*? 
    "'''  # 需要过滤html标签信息在此进行添加
    txt_code = '</b>|\[|]|!|@|#|\$|%|\^|&|\*|  |\(|\)|\+|\\\\|™|®|<|>'  # 需要过滤特殊符号在此添加
    html_list = list(set(re.findall(html_code, txt)))
    for html in html_list:
        txt = txt.replace(html, ' ')
        print(f'替换{html}--->完毕！')
    txt = re.sub(txt_code, ' ', txt)
    txt = txt.replace('  ', ' ')
    print(txt)
    return txt


def get_kuaidaili():
    """
    https://www.kuaidaili.com/free/
    :return:
    """
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    info_list = []
    for page in range(1, 4):
        url = f'https://www.kuaidaili.com/free/inha/{page}/'
        try:
            response = requests.get(url=url, headers=headers)
            html = etree.HTML(response.text)
            ip_list = html.xpath('''//table[@class='table table-b table-bordered table-striped']//tr/td[1]//text()''')
            port_list = html.xpath('''//table[@class='table table-b table-bordered table-striped']//tr/td[2]//text()''')
            ip_zip = zip(ip_list, port_list)
            for ip in ip_zip:
                new_ip = ip[0] + ':' + ip[1]
                info_list.append(new_ip)
            time.sleep(3)
        except Exception as e:
            print(e)
    return list(set(info_list))


def get_pro_list():
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = 'http://proxylist.fatezero.org/proxy.list'
    try:
        response = requests.get(url=url, headers=headers)
        ip_list = re.findall('"host": "(.*?)"', response.text)
        port_list = re.findall('"port": (.*?),', response.text)
        ip_zip = zip(ip_list, port_list)
        for ip in ip_zip:
            new_ip = ip[0] + ':' + ip[1]
            info_list.append(new_ip)
    except Exception as e:
        print(e)
    return list(set(info_list))


def get_ip3366():
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = 'http://www.ip3366.net/'
    try:
        response = requests.get(url=url, headers=headers)
        html = etree.HTML(response.text)
        ip_list = html.xpath('''//table[@class='table table-bordered table-striped']//tr/td[1]//text()''')
        port_list = html.xpath('''//table[@class='table table-bordered table-striped']//tr/td[2]//text()''')
        ip_zip = zip(ip_list, port_list)
        for ip in ip_zip:
            new_ip = ip[0] + ':' + ip[1]
            info_list.append(new_ip)
    except Exception as e:
        print(e)
    return list(set(info_list))


def xiaojie():
    info_list = []
    url = 'https://decode.xiaojieapi.com/api/proxy.php'
    try:
        response = requests.get(url).json()
        for proxy in response['proxy']:
            ip = proxy['ip'] + ":" + proxy['port']
            info_list.append(ip)
    except Exception as e:
        print(e)
    return list(set(info_list))


def ip_main():
    ip_list = get_kuaidaili() + get_pro_list() + get_ip3366() + xiaojie()
    return ip_list


def verfy_ip(ip):
    """
    判断ip有效性
    :param ip:
    :return:
    """
    url = 'https://httpbin.org/get'
    num = 0
    while True:
        num += 1
        if num == 10:
            break
        try:
            proxies = {
                "http": f"http://{ip}",
                "https": f"http://{ip}",
            }
            requests.get(url, proxies=proxies, timeout=10)
            # origin = json.loads(response)["origin"]
            # if str(origin) in str(ip):
            info_ip.append(ip)
        except Exception as e:
            print(f'验证{ip}失败:{e}, 进行第{num}次尝试验证...')


def new_main():
    """
    实时货币功能
    :return:
    """
    key_list = ['美元', '欧元', '英镑', '日元', '澳元', '加元', '港元']
    timestamp = int(time.time() * 1000)
    headers = {
        "Referer": "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=88093251_42_hao_pg&wd=%E5%AE%9E%E6%97%B6%E6%B1%87%E7%8E%87&fenlei=256&rsv_pq=0xd2c6b0be00002071&rsv_t=e1bdGHfcieWM8d6CEYiR9kMsdjsQ5hyAGkarq3H6WgHTme09E%2FTJV%2FXXso%2F%2B&rqlang=en&rsv_dl=tb&rsv_enter=1&rsv_sug3=11&rsv_sug1=11&rsv_sug7=100&rsv_sug2=0&rsv_btype=i&prefixsug=%25E5%25AE%259E%25E6%2597%25B6%25E6%25B1%2587%25E7%258E%2587&rsp=7&inputT=2088&rsv_sug4=2088",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    info_list = []
    for key in key_list:
        url = "https://sp0.baidu.com/5LMDcjW6BwF3otqbppnN2DJv/finance.pae.baidu.com/vapi/async"
        params = {
            "from_money": f"{key}",
            "to_money": "人民币",
            "from_money_num": "1",
            "srcid": "5293",
            "sid": "26350",
            "cb": f"jsonp_{timestamp}_89470"
        }
        response = requests.get(url=url, headers=headers, params=params)
        new_exch = re.findall(f'"exchange_desc2":"1人民币=(.*?){key}"', response.text)[0]
        info = '1人民币=' + new_exch + key
        info_list.append(info)
    return info_list


@st.cache_data
def get_douyin_id(url):
    """
    获取抖音视频id
    :param url:
    :return:
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.url


@st.cache_data
def douyin_video(url):
    """
    抖音无水印视频
    :param url:
    :return:无水印链接, 视频源码, 作者, 视频名称
    """
    urls = get_douyin_id(url)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    code = 0
    while True:
        if code == 5:
            return None
        try:
            url_id = re.findall('(\d\d\d\d\d\d\d\d+)', urls)[0]
            url = f'https://www.douyin.com/discover?modal_id={url_id}'
            response = requests.get(url, headers=headers)
            re_html = re.findall('type="application/json">(.*?)</script>', response.text)[0]
            decode_html = urllib.parse.unquote(re_html)  # 对html进行解码
            video_name = re.findall('"desc":"(.*?)"', decode_html)[0]
            auth = re.findall('"enterpriseVerifyReason":"(.*?)"', decode_html)[0]
            video_url = 'https://' + re.findall('"playApi":"//(.*?)"', decode_html)[0]
            video_content = requests.get(url=video_url, headers=headers).content
            print(f'{video_name}无水印视频链接：{video_url}, {auth}')
            return video_url, video_content, auth, video_name
        except Exception as e:
            print(e)
            code += 1


@st.cache_data  # 装饰器缓存，加快效率
def news_info(urls):
    """
    获取新闻信息
    :param urls:新闻链接
    :return:
    """
    article = Article(urls)
    article.download()
    article.parse()
    if not article.text:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        }
        response = requests.get(url=urls, headers=headers)
        response.encoding = 'utf-8'
        html = etree.HTML(response.text)
        title = html.xpath('//h1//text()')[0]
        content = '\n'.join(html.xpath('//p//text()'))
        if '�' in content:
            response.encoding = 'gbk'
            html = etree.HTML(response.text)
            title = html.xpath('//h1//text()')[0]
            content = '\n'.join(html.xpath('//p//text()'))
        return title, content
    return article.title, article.text


@st.cache_data  # 装饰器缓存，加快效率
def get_img_url_list():
    """
    采集图片
    :return:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    url = f'https://pic.netbian.top/shoujibizhi/index_{random.randint(2, 286)}.html'
    response = requests.get(url, headers=headers)
    href_list = []
    for href in re.findall('data-original="(.*?)"', response.text):
        if "http" in href:
            href_list.append(href)
        else:
            href_list.append("'https:" + href)
    return href_list


@st.cache_data  # 装饰器缓存，加快效率
def get_video_id(kid):
    """
    youtube视频采集
    :param kid: 视频链接
    :return:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    url = f'https://www.youtube.com/embed/{kid}'
    num = 0
    while True:
        if num == 5:
            return None
        try:
            response = requests.get(url=url, headers=headers)
            ids = re.findall('"INNERTUBE_API_KEY":"(.*?)"', response.text)[0]
            return ids
        except Exception as e:
            print(f'video_id:{e}')
            num += 1


@st.cache_data  # 装饰器缓存，加快效率
def get_info(kid, vid):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }
    url = "https://www.youtube.com/youtubei/v1/player"
    params = {
        "key": f"{vid}",
        "prettyPrint": "false"
    }
    data = {
        "context": {
            "client": {
                "hl": "zh-CN",
                "gl": "SG",
                "remoteHost": "192.53.117.115",
                "deviceMake": "",
                "deviceModel": "",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36,gzip(gfe)",
                "clientName": "WEB_EMBEDDED_PLAYER",
                "clientVersion": "1.20230829.01.00",
                "osName": "Windows",
                "osVersion": "10.0",
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "timeZone": "Asia/Shanghai",
                "browserName": "Chrome",
                "browserVersion": "116.0.0.0",
                "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                "connectionType": "CONN_CELLULAR_3G",
                "playerType": "UNIPLAYER",
            },
        },
        "videoId": f"{kid}",
    }
    video_list = []
    codes = 0
    while True:
        if codes == 5:
            return None
        try:
            response = requests.post(url=url, headers=headers, params=params, data=json.dumps(data))
            info_json = response.json()['streamingData']['formats']
            for info in info_json:
                info_dict = {
                    "视频链接": info['url'],
                    "视频画质": info['qualityLabel'],
                    "视频帧率": info['fps'],
                }
                video_list.append(info_dict)
            return video_list
        except Exception as e:
            codes += 1
            print(f'获取视频失败：{e}')


def json_convert_sql(info: dict) -> str:
    """
    json转数据表
    :param info:
    :return:
    """
    text_list = ['CREATE TABLE table_name (', "`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',"]
    for i in info.items():
        info_key = i[0]
        info_value = i[1]
        if len(info_value) >= 100:
            text = f"`{info_key}` text COMMENT '',"
            text_list.append(text)
        elif type(info_key) == int:
            text = f"`{info_key}` int COMMENT '',"
            text_list.append(text)
        else:
            text = f"`{info_key}` varchar(255) COMMENT '',"
            text_list.append(text)
    text_list.append("`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',")
    text_list.append(
        "`updata_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',")
    text_list.append('PRIMARY KEY (`id`)')
    text_list.append(') ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;')
    mysql_sql = '\n'.join(text_list)
    return mysql_sql


def param_url(urls):
    """
    url参数提取
    :param urls:
    :return:
    """
    text = ''
    split_url = urls.split('?')
    url = split_url[0]
    param_spilt = split_url[1].split('&')
    param_dict = {}
    text += f'url = "{url}"\n'
    for p in param_spilt:
        info = p.split('=')
        param_dict[info[0]] = urllib.parse.unquote(info[1].encode('utf-8'))
    # print(param_dict)
    text += f'params = {json.dumps(param_dict, indent=4, ensure_ascii=False, sort_keys=True)}'
    return text


def pdf_word(file) -> (str, str):
    """
    pdf转word
    :return:
    """
    name = file.name.split('.')[0]
    pdf = pdfplumber.open(file)
    page = len(pdf.pages)
    texts = ""
    for i in range(0, page):
        page = pdf.pages[i]
        text = page.extract_text()
        texts += text
    down_name = name + '.docx'
    return down_name, texts


def format_headers(headers: str) -> json:
    """
    header格式化功能
    :param headers:复制的header文本
    :return: 格式化完毕后的json文本
    """
    try:
        split_headers = headers.split('\n')
        new_headers_dict = {}
        for header in split_headers:
            info = header.split(':')
            if len(info) >= 3:
                new_headers_dict.update({info[0].replace(':', ''): info[1].replace('"', '').strip() + ':' + info[2]})
            else:
                new_headers_dict.update({info[0].replace(':', ''): info[1].replace('"', '').strip()})
        return json.dumps(new_headers_dict)
    except Exception as e:
        print(e)
        return None


def get_article(keyword):
    """
    获取文章
    :param keyword:
    :return:
    """
    headers = {
        "referer": "https",
        "sec-ch-ua": "Chromium;v=116, Not)A;Brand;v=24, Google Chrome;v=116",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    url = 'https://so.ruiwen.com/res/best_kds/'
    params = {
        "keyword": f"{keyword}",
        "nhl": "1",
        "page": "1",
        "url": "www.ruiwen.com",
        "v": "2"
    }
    response = requests.get(url, headers=headers, params=params)
    urls = response.json()['data'][0]['url']
    return parse_article(urls)


def parse_article(url):
    """
    解析文章链接
    :param url:
    :return:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_info = str(soup.findAll(name="div", attrs={"class": "main-left"})[0])
    re_str = '<a href="(.*?)"|<img alt(.*?)>|<li class="excellent_articles_title">(.*?)</li>|target="_blank">|<span(.*?)</span>|target="_blank" title="(.*?)">'
    article = re.sub(re_str, '', article_info)
    return article


def query_ip_info(ips):
    """
    查询ip位置
    :param ips:
    :return:
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = "https://nordvpn.com/wp-admin/admin-ajax.php"
    params = {
        "action": "get_user_info_data",
        "ip": f"{ips}"
    }
    response = requests.get(url=url, headers=headers, params=params)
    ip_json_info = {
        'ip': response.json()['ip'],
        'ip服务器': response.json()['isp'],
        '国家': response.json()['country_code'],
        '城市': response.json()['city'],
    }
    lat_long = [response.json()['coordinates']['latitude'], response.json()['coordinates']['longitude']]
    return ip_json_info, lat_long


@st.cache_data  # 装饰器缓存，加快效率
def mv_type(keyword):
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    data = {
        "condition": f"{keyword}",
        "pageSize": 10,
        "pageNum": 1
    }
    url = 'https://www.qmtv.pro/api/app/movie/index/searchMovieByName'
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    mv_list = response.json()['data']['records']
    condition_list = []
    for mv in mv_list:
        condition_list.append(
            [{"movieName": mv['name'], "movieType": mv['type'], "movieYear": mv['year']}, [mv['name'], mv['cover']]])
    return condition_list


@st.cache_data  # 装饰器缓存，加快效率
def get_mv_url(condition, info):
    """
    获取电影信息
    :return:
    """
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    url = 'https://www.qmtv.pro/api/app/movie/website/page'
    data = {"pageSize": 10, "pageNum": 1,
            "condition": condition}
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    info_list = response.json()['data']['records']
    title = info[0]
    mv_img = info[1]
    mv_list = []
    for infos in info_list:
        urls = infos['playUrl']
        mv_list.append(urls)
    return title, mv_img, mv_list


def day_content():
    """
    每日随意一言
    :return:
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
    }
    url = 'https://v1.hitokoto.cn/'
    response = requests.get(url=url, headers=headers).json()["hitokoto"]
    with st.sidebar:
        st.header('每日一言')
        st.write(response)


def translate(txt, language):
    """
    翻译
    :return:
    """
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Content-Length": "7986",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6ImtKMGRHQnQwdnZENHFKNklWbCtvUlE9PSIsInZhbHVlIjoiY1JwMW5nMFkrRFJzcFQxWUVUV0JkaWR5c3Q2bEh1UVY3UGx2ZGRSenNTSFRLQThzNHc1Vmx1Q1crbm90OXZPRzJFRnpFTkhCRWZMV3NSbmF5di95T0cxMmRuK0NmSmpJd1hYM3pJb3MvbjhGVGdTRzRXdW9FZm5TZG1mbzhrUjlkcDYxbXZKYXc1Z2oyYk9vTUFsYmhIZGprTFJNcXZ3UHJrMkxQV1JmSzc0ZWVPbWxXTUg2TTgyY1F6MXZIek5rejJwbXlmelB2c2dCV2VLZVhsUUxKcTQvcGRrTm1kYzF0RVZxL3pHTVhSND0iLCJtYWMiOiIzNDgzYjc1ZDViZDNjZWQ4NzhlMGFmMTU2YmUwYTY0ZTkzNzNkY2UzNjdjODNlMTU4YzBjNjg2ZmRkOTExODhiIn0%3D; XSRF-TOKEN=eyJpdiI6Ijc5alEvY3ZLckFPTGpsOWY1NkxQdFE9PSIsInZhbHVlIjoiTXdpQU9jcDBkd1g0c1FmYmkzdWY2SVo2UjFNZlUxMDFjV0l0WklPaVp1SEJVZTFHS2FHcE41NFpGMFZ4anhvYlpVanpRWjZndi9FYkJQNFA2S0NMbjNOdkcrVFRac3RSY0dvTWRCRW9wOTR5aFp2bG53WTJBTVdjWGNHWkowSGkiLCJtYWMiOiJiZjdhM2MyNTUyM2UyNzM4NmZkMGMyZjU4YjMyZDA2YjM3N2I5MDFlYjE3ZTljNmQwYWUyNTdkNDMxZjhkYWVjIn0%3D; aicc_session=eyJpdiI6InNJT0k2QkUvbkQyeEsvSk9OWEMyTlE9PSIsInZhbHVlIjoiVk5VUjREeWFXT3FuSUYwbC9HczBvSCsxSHBtRzBUNVNuVTdVdGlyOVp0TGRkR3ZCK01SUEFDOXZyYnNsejc4RnFlWmxhRGs5YVlPWG5iNGFhd0FFUno5SlNZZlVsZEpyMUZjZmtqcXBsTG4vekVBckRlNmh0Q0Zub2hmbDJMS2kiLCJtYWMiOiJlYzIwMjZlMzBkMGI3NzgwMGY3MmRjZTM1MDQ3ZjY5ZDk4ZjUyMDkzYzhmYTJiMTM0YTRjYjQ1ODEzOTBlMGM3In0%3D",
        "Host": "free.ai.cc",
        "Origin": "https://free.ai.cc",
        "Referer": "https://free.ai.cc/translate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43",
        "X-CSRF-TOKEN": "oBbCeMQYxUEwmYCW5H956Pe18ofh6N26FdZ3UeMJ",
        "X-Requested-With": "XMLHttpRequest"
    }

    url = 'https://free.ai.cc/trans'
    data = {
        "text": f"{txt}",
        "tl": f"{language}",
        "_token": "oBbCeMQYxUEwmYCW5H956Pe18ofh6N26FdZ3UeMJ"
    }
    response = requests.post(url=url, headers=headers, data=data).json()
    status = response['status']
    if status == 200:
        return response['data']['result']
    else:
        return None


class Tool_Web:
    """
    工具页面
    """
    def __init__(self):

        self.function_type = None  # 功能类别
        self.selectbox_options = (
            "Headers格式化",  # 0
            "Json格式转数据表",  # 1
            "Url参数提取",  # 2
            "新闻采集",  # 3
            "PDF转Word",  # 4
            "图片采集",  # 5
            "Youtube视频采集",  # 6
            "抖音去水印",  # 7
            "Json格式化",  # 8
            "文章采集",  # 9
            "ip代理测试",  # 10
            "长文本换行转python列表",  # 11
            "ip位置查询",  # 12
            "电影搜索",  # 13
            "HTML在线加载",  # 14
            "实时货币",  # 15
            "ip代理获取",  # 16
            "GPT问答",  # 17
            "古诗文查询",  # 18
            "文章过滤杂志",  # 19
            "帮忙做决定",  # 20
            "薪资查询",  # 21
            "每日热榜",  # 22
            "翻译",  # 23
            "qq号等信息查询",  # 24
            "京东商品历史价格查询",  # 25
        )  # 侧边栏参数


    def streamlit_selectbox(self):
        """
        侧边栏初始化
        :return:
        """
        tool_selectbox = st.sidebar.selectbox(
            label="功能列表",
            options=self.selectbox_options
        )
        return tool_selectbox

    def self_header(self):
        if self.function_type == self.selectbox_options[0]:
            '''Headers格式化'''
            st.title(f'{self.selectbox_options[0]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_area(label='请输入需要格式化的header:')
                button_code = st.button(label=':blue[格式化]')
            if button_code:
                with st.sidebar:
                    with st.spinner('正在格式化...'):
                        headers_fun = format_headers(input_message)
                if headers_fun:
                    st.json(headers_fun)
                    with st.sidebar:
                        st.success('格式化完成!')
                else:
                    with st.sidebar:
                        st.error('格式化失败')
                    st.json({"User-Agent": "Mozil   la/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})

    def article_info(self):
        if self.function_type == self.selectbox_options[9]:
            '''文章采集'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_input(label='输入查询的文章类型:')
                button_code = st.button(label=':blue[查询]')
            if button_code:
                with st.sidebar:
                    with st.spinner('正在查询...'):
                        articles = get_article(input_message)
                        st.success('查询成功!')
                st.markdown(articles, unsafe_allow_html=True)

    def self_json_table(self):
        if self.function_type == self.selectbox_options[1]:
            '''Json格式转数据表'''
            st.title(f'{self.selectbox_options[1]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_area(label='请输入需要转换的json:')
                button_code = st.button(label=':blue[转换]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在转换...'):
                            table = json_convert_sql(json.loads(input_message))
                            st.success('转换成功!')
                    st.code(table, language='sql')
                except Exception as e:
                    st.error(f'转换失败：{e}')

    def self_format_json(self):
        if self.function_type == self.selectbox_options[8]:
            '''Json格式化'''
            st.title(self.selectbox_options[8])
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_area(label='请输入需要转换的json:')
                button_code = st.button(label=':blue[转换]')
            if button_code:
                json_info = json.dumps(input_message, indent=4, ensure_ascii=False, sort_keys=True)
                st.json(json.loads(json_info))

    def self_param_url(self):
        if self.function_type == self.selectbox_options[2]:
            '''Url参数提取'''
            st.title(f'{self.selectbox_options[2]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_input(label='请输入需要提取的url:')
                button_code = st.button(label=':blue[提取]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在提取...'):
                            urls = param_url(input_message)
                            st.success('提取成功!')
                    st.code(urls)
                except Exception as e:
                    p_text = "param = {}"
                    text = f"url = {input_message} \n{p_text}"
                    st.code(text)
                    print(e)

    def self_pdf_word(self):
        if self.function_type == self.selectbox_options[4]:
            '''PDF转Word'''
            button_code = 0
            st.title(f'{self.selectbox_options[4]}')
            with st.sidebar:
                file = st.file_uploader("请上传文件", type="pdf")
                if file:
                    with st.spinner('正在上传...'):
                        st.success('文件上传完毕')
                        button_code = st.button(':blue[转换]')
            if button_code:
                pdf_info = pdf_word(file)
                st.text(pdf_info[1])
                with st.sidebar:
                    st.download_button('保存为Word', pdf_info[1], file_name=f'{pdf_info[0]}')

    def self_news(self):
        if self.function_type == self.selectbox_options[3]:
            '''新闻采集'''
            # st.title(f'{self.selectbox_options[3]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_input(label='请输入采集的链接:')
                button_code = st.button(label=':blue[采集]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在采集...'):
                            news_fun = news_info(input_message)
                    st.title(news_fun[0])
                    st.write(news_fun[1])
                except Exception as e:
                    st.error(f'抓取失败：{e}')

    def self_imgs(self):
        if self.function_type == self.selectbox_options[5]:
            '''图片采集'''
            st.title(f'{self.selectbox_options[5]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                # input_message = st.text_input(label='请输入:')
                button_code = st.button(label=':blue[采集]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在采集...'):
                            img_list = get_img_url_list()
                    for imgs in img_list:
                        st.image(imgs)
                except Exception as e:
                    st.error(f'抓取失败：{e}')

    def self_youtube_video(self):
        if self.function_type == self.selectbox_options[6]:
            '''youtube采集'''
            st.title(f'{self.selectbox_options[6]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_input(label='请输入视频链接:')
                button_code = st.button(label=':blue[采集]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在采集...'):
                            kids = re.findall('v=(.*)', input_message)[0]
                            vids = get_video_id(kids)
                            if vids:
                                video_url_list = get_info(kids, vids)
                                st.success('右击视频保存')
                            else:
                                st.error(f'抓取失败')
                    if video_url_list:
                        for video in video_url_list:
                            st.header(f"画质:{video['视频画质']} 帧率:{video['视频帧率']}")
                            st.video(video['视频链接'])
                    else:
                        st.error(f'抓取失败')
                except Exception as e:
                    st.error(f'抓取失败：{e}')

    def self_douyin_video(self):
        if self.function_type == self.selectbox_options[7]:
            '''抖音去水印'''
            # st.title(f'{self.selectbox_options[7]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_input(label='请输入视频链接:')
                urls = re.findall('(https://v.douyin.com/.*?/)', input_message)
                if urls:
                    new_urls = urls[0]
                else:
                    new_urls = input_message
                button_code = st.button(label=':blue[采集]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在采集...'):
                            douyin_video_url = douyin_video(new_urls)
                            if douyin_video_url:
                                st.success('抓取成功')
                            else:
                                st.error(f'抓取失败')
                    if douyin_video_url:
                        video_info = douyin_video_url
                        st.header(video_info[3])
                        st.write(f'作者:{video_info[2]}')
                        st.write(f'无水印视频链接：{video_info[0]}')
                        st.video(video_info[1])
                        st.download_button('保存', data=douyin_video_url[1], file_name='抖音无水印.mp4')
                    else:
                        st.error(f'抓取失败')
                except Exception as e:
                    st.error(f'抓取失败：{e}')

    def test_ip(self):
        if self.function_type == self.selectbox_options[10]:
            '''代理测试'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                ips = st.text_input(label='请输入需要测试的代理ip:')
                button_code = st.button(label=':blue[测试]')
            if button_code:
                with st.sidebar:
                    with st.spinner('正在测试ip是否可用...'):
                        if ips:
                            proxies = {
                                "http": f"http://{ips}",
                                "https": f"http://{ips}",
                            }
                            url = 'https://httpbin.org/get'
                            try:
                                start_time = time.time()
                                response = requests.get(url=url, proxies=proxies, timeout=15)
                                st.success('测试完毕')
                                end_time = time.time() - start_time
                            except Exception as e:
                                response = None
                                st.error(f'测试失败:{e}')
                        else:
                            start_time = time.time()
                            url = 'https://httpbin.org/get'
                            response = requests.get(url=url)
                            st.success('测试完毕')
                            end_time = time.time() - start_time
                if response:
                    st.json(response.json())
                    st.success(f'响应时间：{end_time}')

    def txt_for_list(self):
        if self.function_type == self.selectbox_options[11]:
            '''文本转列表'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                texts = st.text_area(label='请输入需要转换的列表(必须有换行):')
                button_code = st.button(label=':blue[转换]')
            if button_code:
                text_json = {}
                try:
                    texts_spilt = texts.split('\n')
                    text_json['code'] = '1'
                    text_json['list'] = texts_spilt
                    st.success('转换成功！')
                    st.json(text_json)
                except Exception as e:
                    st.error(f'转换失败:{e}')
                    st.json(text_json)

    def isp_area(self):
        if self.function_type == self.selectbox_options[12]:
            '''ip位置查询'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                texts = st.text_input(label='请输入需要查询的ip(请去掉ip的端口):')
                button_code = st.button(label=':blue[查询]')
            if button_code:
                with st.sidebar:
                    with st.spinner('正在查询ip位置...'):
                        try:
                            ip_info = query_ip_info(texts)
                            st.success('查询完毕')
                        except Exception as e:
                            ip_info = None
                            st.error(f'查询失败:{e}')
                if ip_info:
                    st.json(ip_info[0])
                    st.map(latitude=ip_info[1][0], longitude=ip_info[1][1])

    def self_mv(self):
        if self.function_type == self.selectbox_options[13]:
            '''电影搜索'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                texts = st.text_input(label='请输入需要搜索的电影名称:')
                button_code = st.button(label=':blue[查询]')
            if button_code:
                mv_list = mv_type(texts)
                for mv in mv_list:
                    try:
                        mv_info = get_mv_url(mv[0], mv[1])
                        if mv_info:
                            title = mv_info[0]
                            mv_img = mv_info[1]
                            st.title(title)
                            st.image(mv_img)
                            for m in mv_info[2]:
                                st.write(f'电影链接：{m}')
                    except Exception as e:
                        print(f'{e}')
                        continue
                with st.sidebar:
                    st.success('查询完毕')

    def html_loading(self):
        if self.function_type == self.selectbox_options[14]:
            '''HTML在线加载'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                texts = st.text_area(label='请输入需要加载的源码:')
                button_code = st.button(label=':blue[执行]')
            if button_code:
                st.markdown(texts, unsafe_allow_html=True)

    def exchange(self):
        if self.function_type == self.selectbox_options[15]:
            '''实时货币'''
            info_list = new_main()
            for info in info_list:
                st.success(info)


    def provide_ip(self):
        if self.function_type == self.selectbox_options[16]:
            '''ip代理提取'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                button_code = st.button(label=':blue[查询]')
            if button_code:
                with st.sidebar:
                    with st.spinner('正在查询ip...'):
                        ip_lists = ip_main()
                queues = queue.Queue()
                st.success(f'共获取到了{len(ip_lists)}条代理')
                st.text(ip_lists)
                for ips in ip_lists:
                    # st.text(f'{ips}已入验证队列...')
                    queues.put(ips)
                st.text(f'所有ip代理已入验证队列...')
                with st.sidebar:
                    with st.spinner('正在验证ip的有效性...'):
                        try:
                            for i in range(len(ip_lists)):
                                name = f'线程{i}解析'
                                threadName = 'Thread' + str(name)
                                Worker(threadName, queues)
                            queues.join()
                            st.success('验证完毕')
                        except Exception as e:
                            st.error(f'验证失败:{e}')
                st.json({'IpList': list(set(info_ip))})

    def gpt(self):
        if self.function_type == self.selectbox_options[17]:
            '''GPT问答'''
            prompt = st.chat_input("请输入问题:")
            if prompt:
                with st.chat_message("user"):
                    st.write(f"问题：{prompt}")
                with st.spinner('正在编写答案'):
                    info = gemini_pro(prompt)
                with st.chat_message("👋"):
                    st.write(f"{info}")

    def poems(self):
        if self.function_type == self.selectbox_options[18]:
            '''古诗文查询'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                texts = st.text_input(label='请输入古诗名称:')
                button_code = st.button(label=':blue[查询]')
            if button_code:
                poems_info = get_poems(texts)
                title = poems_info[0].strip()
                if title:
                    st.header(title)
                else:
                    st.header(texts)
                auth = poems_info[2].strip() + poems_info[1].strip()
                text_list = poems_info[3]
                st.write(auth)
                for txt in text_list:
                    st.write(txt)
                with st.sidebar:
                    st.success('查询完毕')

    def self_re_txt(self):
        if self.function_type == self.selectbox_options[19]:
            '''文章过滤杂志'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                st.success('过滤:<b>|</b>|<a>|</a>|<li>|</li>|<span|</span>|class=".*?"|href=".*?"|"https:.*?"|"http:.*?"|https:.*? |http:.*? |</b>|\[|]|!|@|#|\$|%|\^|&|\*|  |\(|\)|\+|\\\\|™|®|<|>')
                texts = st.text_input(label='请输入需要过滤的内容：')
                button_code = st.button(label=':blue[过滤]')
            if button_code:
                re_info = re_txt(texts)
                st.write(re_info)

    def self_decision(self):
        if self.function_type == self.selectbox_options[20]:
            '''帮忙做决定'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                texts = st.text_input(label='请输入要去做的事情：')
                button_code = st.button(label=':blue[开始]')
            if button_code:
                code = 0
                for i in range(10):
                    code = random.randint(0, 1)
                if code == 1:
                    st.success('去做这件事吧！')
                else:
                    st.success('我告诉你尽量别这样做！')


    def get_prices(self):
        if self.function_type == self.selectbox_options[21]:
            '''薪资查询'''
            job_dict = {'Java': 100101, 'C/C++': 100102, 'PHP': 100103, 'C#': 100106, '.NET': 100107,
                        'Hadoop': 100108, 'Python': 100109, 'Node.js': 100114, 'Golang': 100116,
                        '语音/视频/图形开发': 100121, '全栈工程师': 100123, 'GIS工程师': 100124,
                        '区块链工程师': 100125, 'Android': 100202, 'iOS': 100203, 'JavaScript': 100208,
                        'U3D': 100209, 'Cocos': 100210, 'UE4': 100211, '技术美术': 100212, '前端开发工程师': 100901,
                        '测试工程师': 100301, '自动化测试': 100302, '功能测试': 100303, '性能测试': 100304,
                        '测试开发': 100305, '移动端测试': 100306, '游戏测试': 100307, '硬件测试': 100308,
                        '软件测试': 100309, '渗透测试': 100310, '运维工程师': 100401, '运维开发工程师': 100402,
                        '网络工程师': 100403, '系统工程师': 100404, 'IT技术支持': 100405, '系统管理员': 100406,
                        '网络安全': 100407, '系统安全': 100408, 'DBA': 100409, '技术文档工程师': 100410,
                        '数据采集': 100122, 'ETL工程师': 100506, '数据仓库': 100507, '数据开发': 100508,
                        '数据分析师': 260102, '数据架构师': 100512, '爬虫工程师': 100514, '项目经理/主管': 100601,
                        '项目助理': 100603, '项目专员': 100604, '实施顾问': 100605, '实施工程师': 100606,
                        '需求分析工程师': 100607, '硬件项目经理': 100817, '技术经理': 100701, '技术总监': 100702,
                        '测试经理': 100703, '架构师': 100704, 'CTO': 100705, '运维总监': 100706,
                        '技术合伙人': 100707, '硬件工程师': 100801, '嵌入式软件工程师': 100802, '单片机': 100804,
                        '电路设计': 100805, '驱动开发工程师': 100806, '系统集成': 100807, 'FPGA开发': 100808,
                        'DSP开发': 100809, 'ARM开发': 100810, 'PCB工程师': 100811, '射频工程师': 100816,
                        '光学工程师': 100818, '通信技术工程师': 101001, '通信研发工程师': 101002,
                        '数据通信工程师': 101003, '移动通信工程师': 101004, '电信网络工程师': 101005,
                        '电信交换工程师': 101006, '有线传输工程师': 101007, '无线/射频通信工程师': 101008,
                        '通信电源工程师': 101009, '通信标准化工程师': 101010, '通信项目专员': 101011,
                        '通信项目经理': 101012, '核心网工程师': 101013, '通信测试工程师': 101014,
                        '通信设备工程师': 101015, '光通信工程师': 101016, '光传输工程师': 101017,
                        '光网络工程师': 101018, '售前技术支持': 101201, '售后技术支持': 101202, '数据挖掘': 100104,
                        '搜索算法': 100115, '自然语言处理算法': 100117, '推荐算法': 100118, '算法工程师': 100120,
                        '机器学习': 101301, '深度学习': 101302, '语音算法': 101305, '图像算法': 101306,
                        '算法研究员': 101307, '自动驾驶系统工程师': 101308, '风控算法': 101309,
                        '大模型算法': 101310, '规控算法': 101311, 'SLAM算法': 101312, '电子工程师': 101401,
                        'FAE': 101403, '集成电路IC设计': 101405, '数字IC验证工程师': 101406,
                        '模拟版图设计工程师': 101407, '电子维修技术员': 101408, '自动化': 100803,
                        '电气工程师': 101402, '电气设计工程师': 101404, '产品经理': 110101, '移动产品经理': 110103,
                        '数据产品经理': 110105, '电商产品经理': 110106, '游戏策划': 110107, '产品专员/助理': 110108,
                        '硬件产品经理': 110109, 'AI产品经理': 110110, '化妆品产品经理': 110111,
                        '高级产品管理岗': 110302, '游戏制作人': 110303, '视觉设计师': 120101, '网页设计师': 120102,
                        'UI设计师': 120105, '平面设计': 120106, '3D设计师': 120107, '广告设计': 140603,
                        '多媒体设计师': 120109, '原画师': 120110, 'CAD设计/制图': 120116, '美工': 120117,
                        '包装设计': 120118, '设计师助理': 120119, '动画设计': 120120, '插画师': 120121,
                        '漫画师': 120122, '修图师': 120123, '交互设计师': 120201, '游戏特效': 120111,
                        '游戏界面设计师': 120112, '游戏场景': 120113, '游戏角色': 120114, '游戏动作': 120115,
                        '游戏数值策划': 120303, '系统策划': 120305, '游戏主美术': 120306, '用户研究员': 120302,
                        'UX设计师': 120304, '用户研究经理': 120407, '用户研究总监': 120408, '设计经理/主管': 120401,
                        '设计总监': 120402, '视觉设计总监': 120404, '服装/纺织设计': 300501, '工业设计': 120602,
                        '橱柜设计': 120603, '家具设计': 120604, '家居设计': 120605, '珠宝设计': 120606,
                        '室内设计': 220205, '陈列设计': 120608, '展览/展示设计': 120611, '照明设计': 120612,
                        '家具拆单员': 120613, '用户运营': 130101, '产品运营': 130102, '数据/策略运营': 130103,
                        '内容运营': 130104, '活动运营': 130105, '商家运营': 130106, '品类运营': 130107,
                        '游戏运营': 130108, '网站运营': 130110, '新媒体运营': 130111, '社区运营': 130112,
                        '微信运营': 130113, '线下拓展运营': 130116, '国内电商运营': 130117, '运营助理/专员': 130118,
                        '内容审核': 130120, '数据标注/AI训练师': 130121, '直播运营': 130122, '车辆运营': 130123,
                        '跨境电商运营': 130124, '淘宝运营': 130126, '天猫运营': 130127, '京东运营': 130128,
                        '拼多多运营': 130129, '亚马逊运营': 130130, '速卖通运营': 130131, '阿里国际站运营': 130132,
                        '亚马逊产品开发': 130133, '视频运营': 170108, '主编/副主编': 130201, '文案编辑': 130203,
                        '网站编辑': 130204, '售前客服': 130301, '售后客服': 130302, '网络客服': 130303,
                        '客服经理': 130304, '客服专员': 130305, '客服主管': 130306, '电话客服': 130308,
                        '运营总监': 130402, 'COO': 130403, '客服总监': 130404, '运营经理/主管': 130405,
                        '网络推广': 130109, '市场营销': 140101, '市场策划': 140102, '市场顾问': 140103,
                        '市场推广': 140104, 'SEO': 140105, 'SEM': 140106, '商务渠道': 140107,
                        '商业数据分析': 140108, '活动策划执行': 140109, '网络营销': 140110, '海外市场': 140111,
                        'APP推广': 140113, '选址开发': 140114, '游戏推广': 140115, '信息流优化师': 140116,
                        '营销主管': 140315, '品牌公关': 140203, '媒介专员': 140204, '媒介经理/总监': 140206,
                        '市场总监': 140401, 'CMO': 140404, '公关总监': 140405, '创意总监': 140407,
                        '会议活动策划': 140502, '会议活动执行': 140503, '会展活动策划': 140505,
                        '会展活动执行': 140506, '广告客户执行': 140202, '广告创意策划': 140601, '美术指导': 170202,
                        '策划经理': 170204, '广告文案': 170205, '广告制作': 170207, '媒介投放': 170208,
                        '媒介商务BD': 140609, '广告审核': 170211, '广告/会展项目经理': 170212, '政府关系': 140112,
                        '政策研究': 140801, '企业党建': 140802, '社工': 140803, '项目申报专员': 140804,
                        '招聘': 150102, 'HRBP': 150103, '人力资源专员/助理': 150104, '培训': 150105,
                        '薪酬绩效': 150106, '人力资源总监': 150108, '员工关系': 150109, '组织发展': 150110,
                        '企业文化': 150111, '人力资源经理/主管': 150403, '行政专员/助理': 150201, '前台': 150202,
                        '经理助理': 150205, '后勤': 150207, '行政总监': 150209, '文员': 150210,
                        '行政经理/主管': 150401, '会计': 150301, '出纳': 150302, '财务顾问': 150303,
                        '结算会计': 150304, '税务': 150305, '审计': 150306, '财务总监/VP': 150308,
                        '成本会计': 150310, '总账会计': 150311, '建筑/工程会计': 150312, '税务外勤会计': 150313,
                        '统计员': 150314, '财务分析/财务BP': 150316, '财务经理/主管': 150402, 'CFO': 150404,
                        '法务专员/助理': 150203, '律师': 150502, '法律顾问': 150504, '法务经理/主管': 150506,
                        '法务总监': 150507, '销售专员': 140301, '客户代表': 140303, '大客户代表': 140304,
                        'BD经理': 140305, '渠道销售': 140307, '电话销售': 140310, '网络销售': 140314,
                        '销售工程师': 140316, '客户经理': 180403, '销售经理': 140302, '销售总监': 140402,
                        '区域总监': 160101, '城市经理': 160102, '销售VP': 160103, '团队经理': 160104,
                        '销售运营': 130119, '销售助理': 140309, '商务总监': 140403, '商务专员': 160301,
                        '商务经理': 160302, '客户成功': 160303, '服装导购': 160501, '化妆品导购': 210406,
                        '美容顾问': 210414, '瘦身顾问': 210602, '会籍顾问': 210610, '旅游顾问': 280103,
                        '珠宝销售': 290312, '汽车销售': 230201, '汽车配件销售': 230202, '广告销售': 140313,
                        '会议活动销售': 140501, '会展活动销售': 140504, '信用卡销售': 180401, '理财顾问': 180506,
                        '保险顾问': 180701, '证券经纪人': 180801, '外贸经理': 250201, '外贸业务员': 250203,
                        '课程顾问': 190601, '招生顾问': 190602, '留学顾问': 190603, '医药代表': 210502,
                        '健康顾问': 210504, '医美咨询': 210505, '医疗器械销售': 210506, '口腔咨询师': 210507,
                        '记者/采编': 170101, '编辑': 170102, '作者/撰稿人': 170104, '出版发行': 170105,
                        '校对录入': 170106, '印刷排版': 170109, '广告创意设计': 170201, '媒介合作': 170209,
                        '导演/编导': 170601, '摄影/摄像师': 170602, '视频编辑': 170603, '音频编辑': 170604,
                        '经纪人/星探': 170605, '后期制作': 170606, '影视发行': 170608, '影视策划': 170609,
                        '主播': 170610, '演员/配音员': 170611, '化妆/造型/服装': 170612, '放映员': 170613,
                        '录音/音效': 170614, '制片人': 170615, '编剧': 170616, '艺人助理': 170617,
                        '主持人/DJ': 170620, '中控/场控/助播': 170621, '灯光师': 170622, '剪辑师': 170623,
                        '影视特效': 170624, '带货主播': 170625, '剧本杀主持人': 170626, '剧本杀编剧': 170627,
                        '儿童引导师': 170628, '游戏主播': 170629, '模特': 170630, '投资经理': 180101,
                        '行业研究': 180103, '投资总监/VP': 180112, '融资': 180115, '并购': 180116,
                        '投后管理': 180117, '投资助理': 180118, '投资者关系/证券事务代表': 180120, '风控': 150307,
                        '资产评估': 180104, '资信评估': 180203, '合规稽查': 180204, '清算': 180304,
                        '金融产品经理': 180501, '催收员': 180503, '柜员': 180402, '银行大堂经理': 180404,
                        '信贷专员': 180406, '保险精算师': 180702, '保险理赔': 180703, '证券交易员': 180106,
                        '卖方分析师': 180802, '买方分析师': 180803, '基金经理': 180805, '投资银行业务': 180806,
                        '量化研究员': 180807, '课程设计': 190101, '课程编辑': 190102, '培训研究': 190104,
                        '培训师': 190503, '培训策划': 190107, '校长/副校长': 190201, '教务管理': 190202,
                        '教学管理': 190203, '班主任/辅导员': 190204, '园长/副园长': 190205, '地理教师': 190245,
                        '教师': 190301, '助教': 190302, '高中教师': 190303, '初中教师': 190304, '小学教师': 190305,
                        '幼教': 190306, '理科教师': 190307, '文科教师': 190308, '英语教师': 190309,
                        '音乐教师': 190310, '美术教师': 190311, '体育教师/体育教练': 190312, '就业老师': 190313,
                        '日语教师': 190314, '其他外语教师': 190315, '语文教师': 190316, '数学教师': 190317,
                        '物理教师': 190318, '化学教师': 190319, '生物教师': 190320, '家教': 190321,
                        '托管老师': 190322, '早教老师': 190323, '感统训练教师': 190324, '保育员': 190326,
                        'JAVA培训讲师': 190401, 'Android培训讲师': 190402, 'iOS培训讲师': 190403,
                        'PHP培训讲师': 190404, '.NET培训讲师': 190405, 'C++培训讲师': 190406,
                        'Unity 3D培训讲师': 190407, 'Web前端培训讲师': 190408, '软件测试培训讲师': 190409,
                        '动漫培训讲师': 190410, 'UI设计培训讲师': 190411, '财会培训讲师': 190501,
                        '拓展培训': 190504, '舞蹈老师': 190701, '瑜伽老师': 210601, '游泳教练': 210603,
                        '健身教练': 190705, '篮球教练': 190706, '跆拳道教练': 190707, '武术教练': 190708,
                        '轮滑教练': 190709, '表演教师': 190710, '机器人教师': 190711, '书法教师': 190712,
                        '钢琴教师': 190713, '吉他教师': 190714, '古筝教师': 190715, '播音主持教师': 190716,
                        '乐高教师': 190717, '少儿编程老师': 190718, '乒乓球教练': 190719, '羽毛球教练': 190720,
                        '足球教练': 190766, '架子鼓老师': 190767, '围棋老师': 190768, '拳击教练': 190769,
                        '医药研发': 210108, '生物学研究人员': 210115, '药品注册': 210116, '药品生产': 210117,
                        '医药项目经理': 210123, '细胞培养员': 210124, '药物分析': 210125, '药物合成': 210126,
                        '医疗产品技术支持': 210127, '生物信息工程师': 210128, '制剂研发': 210129, '护士': 210201,
                        '护士长': 210202, '导医': 210503, '药剂师': 210104, '验光师': 210109, '检验科医师': 210111,
                        '医生助理': 210112, '放射科医生': 210113, '超声科医生': 210114, '中医': 210302,
                        '精神心理科医生': 210303, '口腔科医生': 210304, '内科医生': 210306, '全科医生': 210307,
                        '幼儿园保健医': 210308, '外科医生': 210309, '儿科医生': 210310, '妇产科医生': 210311,
                        '眼科医生': 210312, '皮肤科医生': 210313, '耳鼻喉科医生': 210314, '麻醉科医生': 210315,
                        '病理科医生': 210316, '医务管理': 210317, '整形医生': 210402, '康复治疗师': 210305,
                        '营养师/健康管理师': 210401, '药店店长': 210801, '执业药师/驻店药师': 210802,
                        '药店店员': 210803, '医疗器械研发': 210105, '医疗器械注册': 210121,
                        '医疗器械生产/质量管理': 210122, '试剂研发': 210901, '临床医学经理/专员': 210118,
                        '临床协调员': 210119, '临床数据分析': 210120, '临床医学总监': 210501,
                        '临床项目经理': 211001, '临床监查员': 211002, '房地产策划': 220101, '地产项目管理': 220102,
                        '地产招投标': 220103, '房产评估师': 220302, '建筑工程师': 220202, '建筑设计师': 220203,
                        '土木/土建/结构工程师': 220204, '园林/景观设计': 220206, '城市规划设计': 220207,
                        '弱电工程师': 220213, '给排水工程师': 220214, '暖通工程师': 220215, '幕墙工程师': 220216,
                        'BIM工程师': 220221, '建筑机电工程师': 220223, '消防工程师': 220224, '物业经理': 220401,
                        '综合维修工': 220404, '绿化工': 220405, '物业管理员': 220406, '物业工程主管': 220407,
                        '地产项目总监': 220501, '地产策划总监': 220502, '地产招投标总监': 220503,
                        '软装设计师': 220217, '装修项目经理': 220222, '工程监理': 220208, '工程造价': 220209,
                        '工程预算': 220210, '资料员': 220211, '建筑施工项目经理': 220212, '施工员': 220218,
                        '测绘/测量': 220219, '材料员': 220220, '施工安全员': 220225, '供应链专员': 240101,
                        '供应链经理': 240102, '物流专员': 240103, '物流经理': 240104, '物流运营': 240105,
                        '物流跟单': 240106, '调度员': 240108, '物流/仓储项目经理': 240109, '货运代理专员': 240111,
                        '货运代理经理': 240112, '水/空/陆运操作': 240113, '配送站长': 240118, '跟车员': 240119,
                        '集装箱管理': 240302, '仓库主管/经理': 240201, '仓库管理员': 240204, '仓库文员': 240205,
                        '配/理/拣/发货': 240206, '无人机飞手': 100311, '商务司机': 150208, '运输经理/主管': 240110,
                        '货运司机': 240301, '配送员': 240303, '快递员': 240304, '网约车司机': 240305,
                        '代驾司机': 240306, '驾校教练': 240307, '客运司机': 240308, '供应链总监': 240401,
                        '物流总监': 240402, '商品经理': 140312, '采购总监': 250101, '采购经理/主管': 250102,
                        '采购专员/助理': 250103, '买手': 250104, '采购工程师': 250105, '供应商质量工程师': 250108,
                        '招标专员': 250109, '投标专员': 250110, '商品专员/助理': 250111, '报关/报检员': 240114,
                        '单证员': 240117, '贸易跟单': 250204, '企业管理咨询': 260101, 'IT咨询顾问': 260104,
                        '人力资源咨询顾问': 260105, '咨询项目管理': 260106, '战略咨询': 260107, '猎头顾问': 260108,
                        '市场调研': 260109, '其他咨询顾问': 260110, '知识产权/专利/商标代理人': 260111,
                        '心理咨询师': 260112, '婚恋咨询师': 260113, '咨询总监': 260401, '咨询经理': 260402,
                        '专利律师': 150503, '事务所律师': 260201, '法务': 260202, '知识产权律师': 260203,
                        '律师助理': 260204, '英语翻译': 260301, '日语翻译': 260302, '韩语/朝鲜语翻译': 260303,
                        '法语翻译': 260304, '德语翻译': 260305, '俄语翻译': 260306, '西班牙语翻译': 260307,
                        '其他语种翻译': 260308, '计调': 280101, '签证专员': 280102, '导游': 280104,
                        '票务员': 280105, '讲解员': 280106, '旅游产品经理': 280201, '旅游策划师': 280202,
                        '救生员': 210613, '汽车服务顾问': 230203, '汽车维修': 230204, '汽车美容': 230205,
                        '汽车查勘定损': 230206, '二手车评估师': 230207, '4S店店长/维修站长': 230208,
                        '汽车改装工程师': 230209, '洗车工': 230213, '加油员': 230214, '酒店前台': 290102,
                        '客房服务员': 290103, '酒店经理': 290104, '礼仪/迎宾/接待': 290107, '酒店前厅经理': 290115,
                        '客房经理': 290116, '民宿管家': 290158, '收银': 290201, '服务员': 290202, '厨师': 290203,
                        '咖啡师': 290204, '送餐员': 290205, '餐饮店长': 290206, '餐饮前厅经理/领班': 290207,
                        '后厨': 290208, '配菜打荷': 290209, '茶艺师': 290210, '蛋糕/裱花师': 290211,
                        '餐饮学徒': 290212, '面点师': 290213, '行政总厨': 290214, '厨师长': 290215,
                        '传菜员': 290216, '洗碗工': 290217, '凉菜厨师': 290218, '中餐厨师': 290219,
                        '西餐厨师': 290220, '日料厨师': 290221, '烧烤师傅': 290222, '奶茶店店员': 290223,
                        '水台': 290224, '面包/烘焙师': 290225, '餐饮储备店长/干部': 290226, '调酒师': 290227,
                        '导购': 290302, '店员/营业员': 290303, '门店店长': 290304, '督导/巡店': 290305,
                        '陈列员': 290306, '理货员': 290307, '防损员': 290308, '卖场经理': 290309, '促销员': 290311,
                        '商场运营': 290314, '保安': 290105, '保洁': 290106, '保姆': 290108, '月嫂': 290109,
                        '育婴师': 290110, '护工': 290111, '安检员': 290112, '手机维修': 290113, '家电维修': 290114,
                        '保安经理': 290117, '产后康复师': 290118, '押运员': 290120, '消防中控员': 290121,
                        '保洁经理': 290122, '消防维保员': 290123, '电脑维修': 290166, '收纳师': 290169,
                        '宠物美容': 290601, '宠物医生': 290602, '花艺师': 290701, '婚礼策划': 290702,
                        '理疗师': 210403, '针灸推拿': 210404, '美容师': 210405, '纹绣师': 210407, '美体师': 210408,
                        '美发助理/学徒': 210409, '美容店长': 210410, '足疗师': 210411, '按摩师': 210412,
                        '采耳师': 210415, '发型师': 210607, '美甲美睫师': 210608, '化妆/造型师': 210609,
                        '养发师': 290801, '汽车设计': 230101, '车身/造型设计': 230102, '底盘工程师': 230103,
                        '动力系统工程师': 230105, '汽车电子工程师': 230106, '汽车零部件设计': 230107,
                        '汽车项目管理': 230108, '内外饰设计工程师': 230110, '总装工程师': 230210, '厂长': 300101,
                        '生产总监': 300102, '车间主任': 300103, '生产组长/拉长': 300104, '生产设备管理员': 300106,
                        '生产计划/物料管理(PMC)': 300107, '生产文员': 300108, '厂务': 300110,
                        '汽车质量工程师': 230109, '质量管理/测试': 300201, '可靠度工程师': 300202,
                        '失效分析工程师': 300203, '产品认证工程师': 300204, '体系工程师': 300205,
                        '体系审核员': 300206, '生产安全员': 300207, '质检员': 300208, '计量工程师': 300209,
                        '安全评价师': 300210, '热设计工程师': 100813, '机械工程师': 300301,
                        '机械设备工程师': 300303, '机械维修/保养': 300304, '机械制图员': 300305,
                        '机械结构工程师': 300306, '工业工程师(IE)': 300307, '工艺工程师': 300308,
                        '材料工程师': 300309, '机电工程师': 300310, 'CNC/数控': 300311, '冲压工程师': 300312,
                        '夹具工程师': 300313, '模具工程师': 300314, '焊接工程师': 300315, '注塑工程师': 300316,
                        '铸造/锻造工程师': 300317, '液压工程师': 300318, '化工工程师': 300401,
                        '实验室技术员': 300402, '涂料研发': 300404, '化妆品研发': 300405, '食品/饮料研发': 300406,
                        '化工项目经理': 300407, '面料辅料开发': 300507, '打样/制版': 300509,
                        '服装/纺织/皮革跟单': 300510, '量体师': 300511, '普工/操作工': 300601, '叉车工': 300602,
                        '铲车司机': 300603, '焊工': 300604, '氩弧焊工': 300605, '电工': 300606, '木工': 300608,
                        '油漆工': 300609, '车工': 300610, '磨工': 300611, '铣工': 300612, '钳工': 300613,
                        '钻工': 300614, '铆工': 300615, '钣金工': 300616, '抛光工': 300617, '机修工': 300618,
                        '折弯工': 300619, '电镀工': 300620, '喷塑工': 300621, '注塑工': 300622, '组装工': 300623,
                        '包装工': 300624, '空调工': 300625, '电梯工': 300626, '锅炉工': 300627, '学徒工': 300628,
                        '缝纫工': 300629, '搬运工/装卸工': 300630, '切割工': 300631, '样衣工': 300632,
                        '模具工': 300633, '挖掘机司机': 300634, '弱电工': 300635, '裁剪工': 300637,
                        '水电工': 300638, '电池工程师': 300801, '电机工程师': 300802, '线束设计': 300803,
                        '环保工程师': 300901, '环评工程师': 300902, 'EHS工程师': 300903, '碳排放管理师': 300904,
                        '环境检测员': 300905, '地质工程师': 301001, '光伏系统工程师': 301002,
                        '风电运维工程师': 301003, '水利工程师': 301004}
            for key in job_dict.items():
                keys = key[0]
                keys_code = key[1]
                button_code = st.button(label=f':blue[{keys}]')
                if button_code:
                    info = job_info(keys=keys, positionId=keys_code)
                    st.success(info)


    def day_hot_img(self):
        if self.function_type == self.selectbox_options[22]:
            '''每日热榜'''
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
            }
            url = 'https://api.pearktrue.cn/api/60s/image/hot/?type=baidu'
            response = requests.get(url=url, headers=headers).content
            st.image(response)


    def streamlit_translate(self):
        if self.function_type == self.selectbox_options[23]:
            '''实时翻译'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                genre = st.radio(
                    "请选择需要翻译的语言",
                    ["中文", "英文"])
            if genre == '中文':
                st.success("中文转英文")
                language = 'en'
                txt = st.text_input(label='请输入待翻译信息')
                button_code = st.button(label=':blue[翻译]')
                if button_code:
                    translate_info = translate(txt, language)
                    st.write('翻译结果：')
                    st.info(translate_info)
            if genre == '英文':
                language = 'zh'
                st.success('英文转中文')
                txt = st.text_input(label='请输入待翻译信息')
                button_code = st.button(label=':blue[翻译]')
                if button_code:
                    translate_info = translate(txt, language)
                    st.write('翻译结果：')
                    st.info(translate_info)


    def qq_info(self):
        headers = {
            "Referer": "http://xhnzz.xyz/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
        }
        if self.function_type == self.selectbox_options[24]:
            '''qq号等信息查询'''
            with st.sidebar:
                genre = st.radio(
                    "请选择需要查询的信息",
                    ["qq号查询", "手机号查询", "微博uid查询"])

            if genre == 'qq号查询':
                txt = st.text_input(label='请输入qq号')
                button_code = st.button(label=':blue[查询]')
                if button_code:
                    url = f'https://zy.xywlapi.cc/qqcx2023?qq={txt}'
                    response = requests.get(url=url, headers=headers).json()
                    status = response['status']
                    if status == 200:
                        st.text(
                            f"qq:{txt}\n"
                            f"电话:{response['phone']}\n"
                            f"归属地:{response['phonediqu']}\n"
                            f"lol名称:{response['lol']}\n"
                            f"微博id:{response['wb']}\n"
                            f"qq密码:{response['qqlm']}"
                        )
                        if response['wb'] != '没有找到':
                            st.text(f"微博链接:https://www.weibo.com/u/{response['wb']}\n")
                    else:
                        st.text('查询失败')

            if genre == '手机号查询':
                txt = st.text_input(label='请输入手机号')
                button_code = st.button(label=':blue[查询]')
                if button_code:
                    url = f'https://zy.xywlapi.cc/qqxc2023?phone={txt}'
                    response = requests.get(url=url, headers=headers).json()
                    status = response['status']
                    if status == 200:
                        st.text(
                            f"电话:{txt}\n"
                            f"qq:{response['qq']}\n"
                            f"归属地:{response['phonediqu']}\n"
                            f"lol名称:{response['lol']}\n"
                            f"微博id:{response['wb']}\n"
                            f"qq密码:{response['qqlm']}"
                        )
                        if response['wb'] != '没有找到':
                            st.text(f"微博链接:https://www.weibo.com/u/{response['wb']}\n")
                    else:
                        st.text('查询失败')
            if genre == '微博uid查询':
                txt = st.text_input(label='请输入微博uid')
                button_code = st.button(label=':blue[查询]')
                if button_code:
                    url = f'https://api.xywlapi.cc/wbapi?id={txt}'
                    response = requests.get(url=url, headers=headers).json()
                    status = response['status']
                    if status == 200:
                        st.text(
                            f"uid:{txt}\n"
                            f"电话:{response['phone']}\n"
                            f"归属地:{response['phonediqu']}\n"
                        )
                    else:
                        st.text('查询失败')


    def jingdong_price(self):
        if self.function_type == self.selectbox_options[25]:
            '''京东价格查询'''
            with st.sidebar:  # 需要在侧边栏内展示的内容
                st.write('例:https://item.jd.com/10080177096677.html')
                txt = st.text_input(label='请输入需要查询的商品链接')
                button_code = st.button(label=':blue[查询]')
            if button_code:
                if 'https://item.jd.com/' not in txt:
                    st.error('链接错误,请检查输入链接是否正确')
                else:
                    with st.spinner('正在查询...'):
                        goods_info = parse_goods_price(txt)
                    if goods_info:
                        st.info(f"{goods_info['商品名称']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(goods_info['图片'])
                            # st.caption(f"商品链接：{goods_info['链接']}")
                            st.metric(label="对比历史最低价", value=str(int(goods_info['当前价格'])), delta=goods_info['涨幅'])
                            st.caption(f"当前价格：:red[{goods_info['当前价格']}]元")
                            st.caption(f"历史最低价格：:red[{goods_info['最低价格']}]元")
                            st.caption(f"三月内最高价格：:red[{max(goods_info['历史时间段价格'])}]元")

                        with col2:
                            st.caption(f":blue[历史价格表]:")
                            data_df = pd.DataFrame(
                                {
                                    '日期': goods_info['历史时间段'],
                                    '价格': goods_info['历史时间段价格'],
                                },
                            )
                            st.data_editor(
                                data_df,
                                column_config={
                                    "widgets": st.column_config.Column(
                                        "Streamlit Widgets",
                                        help="Streamlit **widget** commands 🎈",
                                        width="small",
                                        required=True,
                                    )
                                },
                            )
                    else:
                        'https://tool.manmanbuy.com/HistoryLowest.aspx?url=https%3a%2f%2fitem.jd.com%2f10080177096677.html'
                        st.error('查询失败,请检查是否出现滑块或者是cookie过期')


    def streamlit_function(self):
        """
        侧边栏执行功能
        :return:
        """
        with st.sidebar:
            response = requests.get('http://116.62.53.121/images/1704683737308.png').content
            st.image(response, caption='赞助作者')

        self.function_type = self.streamlit_selectbox()
        self.self_header()  # headers格式化
        self.self_format_json()  # json格式化
        self.self_json_table()  # json转数据表
        self.self_pdf_word()  # pdf转word
        self.self_param_url()  # url参数提取
        self.self_news()  # 新闻采集
        self.self_imgs()  # 图片采集
        self.article_info()  # 文章采集
        self.self_youtube_video()  # youtube视频采集
        self.self_douyin_video()  # 抖音无水印
        self.test_ip()  # ip测试
        self.txt_for_list()  # 长文本转列表
        self.isp_area()  # ip地址查询
        self.self_mv()  # 电影搜索
        self.html_loading()  # html加载
        self.exchange()  # 实时货币
        self.provide_ip()  # ip代理获取
        self.gpt()  # gpt问答
        self.poems()  # 古诗文查询
        self.self_re_txt()  # 文章过滤杂志
        self.self_decision()  # 帮忙做决定
        self.get_prices()  # 薪资查询
        self.day_hot_img()  # 每日热榜
        self.streamlit_translate()  # 翻译
        self.qq_info()  # qq信息查询
        self.jingdong_price()  # 京东历史价格查询


if __name__ == '__main__':
    info_ip = []
    tool = Tool_Web()
    tool.streamlit_function()
