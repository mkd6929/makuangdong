import requests
import json
import re
import random
import streamlit as st
from newspaper import Article
from urllib import parse
import urllib
from bs4 import BeautifulSoup
import pdfplumber
import time
import threading
import queue
from lxml import etree


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
        response = requests.get(url=url, headers=headers)
        html = etree.HTML(response.text)
        ip_list = html.xpath('''//table[@class='table table-b table-bordered table-striped']//tr/td[1]//text()''')
        port_list = html.xpath('''//table[@class='table table-b table-bordered table-striped']//tr/td[2]//text()''')
        ip_zip = zip(ip_list, port_list)
        for ip in ip_zip:
            new_ip = ip[0] + ':' + ip[1]
            info_list.append(new_ip)
        time.sleep(3)
    return list(set(info_list))


def get_pro_list():
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = 'http://proxylist.fatezero.org/proxy.list'
    response = requests.get(url=url, headers=headers)
    ip_list = re.findall('"host": "(.*?)"', response.text)
    port_list = re.findall('"port": (.*?),', response.text)
    ip_zip = zip(ip_list, port_list)
    for ip in ip_zip:
        new_ip = ip[0] + ':' + ip[1]
        info_list.append(new_ip)
    return list(set(info_list))


def get_ip3366():
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = 'http://www.ip3366.net/'
    response = requests.get(url=url, headers=headers)
    html = etree.HTML(response.text)
    ip_list = html.xpath('''//table[@class='table table-bordered table-striped']//tr/td[1]//text()''')
    port_list = html.xpath('''//table[@class='table table-bordered table-striped']//tr/td[2]//text()''')
    ip_zip = zip(ip_list, port_list)
    for ip in ip_zip:
        new_ip = ip[0] + ':' + ip[1]
        info_list.append(new_ip)
    return list(set(info_list))


def seofangfa():
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    url = 'http://www.ip3366.net/'
    response = requests.get(url=url, headers=headers)
    response.encoding = 'utf-8'
    html = etree.HTML(response.text)
    ip_list = html.xpath('''//tr/td[1]//text()''')
    port_list = html.xpath('''//tr/td[2]//text()''')
    ip_zip = zip(ip_list, port_list)
    for ip in ip_zip:
        new_ip = ip[0] + ':' + ip[1]
        info_list.append(new_ip)
    return list(set(info_list))


def ip_main():
    ip_list = get_kuaidaili() + get_pro_list() + get_ip3366() + seofangfa()
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
            "ip代理获取", # 16
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
                    st.json({
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})

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
                except:
                    p_text = "param = {}"
                    text = f"url = {input_message} \n{p_text}"
                    st.code(text)

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
                input_message = st.text_input(label='请输入:')
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


    def streamlit_function(self):
        """
        侧边栏执行功能
        :return:
        """
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


if __name__ == '__main__':
    info_ip = []
    tool = Tool_Web()
    tool.streamlit_function()
