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
    :return:
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
            print(response.text)
            re_html = re.findall('type="application/json">(.*?)</script>', response.text)[0]
            decode_html = urllib.parse.unquote(re_html)  # 对html进行解码
            video_url = 'https://' + re.findall('"playApi":"//(.*?)"', decode_html)[0]
            print(f'无水印视频链接：{video_url}')
            return video_url
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
    text_list.append("`updata_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',")
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
    st.text(response.text)
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
    re_str = '<a href="(.*?)"|<img alt(.*?)>|<li class="excellent_articles_title">(.*?)</li>|target="_blank">|<span(.*?)</span>'
    article = re.sub(re_str, '', article_info)
    return article


class Tool_Web:
    """
    工具页面
    """

    def __init__(self):
        self.function_type = None  # 功能类别
        self.selectbox_options = (
            "Headers格式化",
            "Json格式转数据表",
            "Url参数提取",
            "新闻采集",
            "PDF转Word",
            "图片采集",
            "Youtube视频采集",
            "抖音去水印",
            "Json格式化",
            "文章采集",
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
                    st.json({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})

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
                    st.code(table)
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
                            print(img_list)
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
            st.title(f'{self.selectbox_options[7]}')
            with st.sidebar:  # 需要在侧边栏内展示的内容
                input_message = st.text_input(label='请输入视频链接:')
                button_code = st.button(label=':blue[采集]')
            if button_code:
                try:
                    with st.sidebar:
                        with st.spinner('正在采集...'):
                            douyin_video_url = douyin_video(input_message)
                            if douyin_video_url:
                                st.success('进入视频链接右键保存')
                            else:
                                st.error(f'抓取失败')
                    if douyin_video_url:
                        st.header('无水印视频链接：')
                        st.write(douyin_video_url)
                        # st.video(douyin_video_url)
                    else:
                        st.error(f'抓取失败')
                except Exception as e:
                    st.error(f'抓取失败：{e}')


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


if __name__ == '__main__':
    tool = Tool_Web()
    tool.streamlit_function()
