import streamlit as st
import json
import urllib
from urllib import parse
from newspaper import Article
import base64
import pdfplumber
import re
import random
import requests


def json_convert_sql(info: dict) -> str:
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


def format_headers(text):
    headers = text
    split_headers = headers.split('\n')
    new_headers_dict = {}
    for header in split_headers:
        info = header.split(':')
        new_headers_dict.update({info[0].replace(':', ''): info[1].replace('"', '').strip()})
    return json.dumps(new_headers_dict)


def st_format_headers(keyword):
    with st.sidebar:
        try:
            header_info = format_headers(text=keyword)
            return header_info
        except Exception as e:
            st.text(f'headers格式化失败：{e}')


def st_sql(sql_name):
    with st.sidebar:
        try:
            return json_convert_sql(json.loads(sql_name))
        except Exception as e:
            st.text(f'{e}')


def st_url(urls):
    with st.sidebar:
        split_url = urls.split('?')
    try:
        url_domain = split_url[0]
        st.text(f'url = "{url_domain}"')
        url_param_list = split_url[1].split('&')
        st.text('param = {')
        for url_param in url_param_list:
            url_param_spilt = url_param.split('=')
            st.text(f'''"{url_param_spilt[0]}": "{urllib.parse.unquote(url_param_spilt[1].encode('utf-8'))}",''')
        st.text('}')
    except:
        st.text('param = {}')

def down_img_content(urls):
    num = 0
    while num < 5:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        }
        try:
            response = requests.get(urls, headers=headers).content
            return response
        except Exception as e:
            num += 1
            print(e)


def get_img_url_list():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    url = f'https://pic.netbian.top/shoujibizhi/index_{random.randint(2, 286)}.html'
    response = requests.get(url, headers=headers)
    href_list = ['https:' + imgs1 for imgs1 in re.findall('data-original="(.*?)"', response.text)]
    return href_list


def news_info(urls):
    article = Article(urls)
    article.download()
    article.parse()
    st.title(article.title)
    st.write(article.text)


def get_video_id(kid):
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


if __name__ == '__main__':
    img_list = []
    imgs = ''


    with st.sidebar:
        st.title('爬虫工具站')
    add_selectbox = st.sidebar.selectbox(
        "功能列表",
        ("Headers格式化", "Json格式转数据表", "Url参数提取", "新闻采集", "PDF转Word", "图片采集", "Youtube视频采集")
    )
    if add_selectbox == 'Headers格式化':
        with st.sidebar:
            add_radio = st.text_area(label='请输入需要格式化的header:')
            button_code = st.button(':blue[格式化]')
        if button_code:
            if add_radio:
                st.json(st_format_headers(add_radio))
            else:
                st.json({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
    if add_selectbox == 'Json格式转数据表':
        with st.sidebar:
            add_radio = st.text_area(label='请输入需要转换的json:')
            button_code = st.button(':blue[转换数据表]')
        if button_code:
            if add_radio:
                st.code(st_sql(add_radio), language='sql')
            else:
                st.code('''CREATE TABLE table_name (
           `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
           `User-Agent` text COMMENT '',
           `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
           `updata_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
           PRIMARY KEY (`id`)
           ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;''')
    if add_selectbox == 'Url参数提取':
        with st.sidebar:
            add_radio = st.text_input(label='请输入需要转换的链接：')
            button_code = st.button(':blue[提取]')
        if button_code:
            if add_radio:
                st_url(add_radio)
            else:
                st.text('''url = ""\nparams = {}''')
    if add_selectbox == '新闻采集':
        with st.sidebar:
            add_radio = st.text_area(label='请输入需要采集的链接:')
            button_code = st.button(':blue[采集]')
        if button_code:
            if add_radio:
                news_info(add_radio)
            else:
                st.text('''抓取失败''')
    if add_selectbox == 'PDF转Word':
        col1, col2 = st.columns([3, 1])
        with st.sidebar:
            file = st.file_uploader("请上传文件", type="pdf")
        if file:
            with col2:
                base64_pdf = base64.b64encode(file.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="550" height="1000" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
        if file:
            with st.sidebar:
                st.write('文件上传完毕')
                button_code = st.button(':blue[转换]')
            with col1:
                if button_code:
                    name = file.name.split('.')[0]
                    pdf = pdfplumber.open(file)
                    page = len(pdf.pages)
                    texts = ""
                    for i in range(0, page):
                        page = pdf.pages[i]
                        text = page.extract_text()
                        texts += text
                    st.header('转换结果:')
                    st.text(texts)
                    with st.sidebar:
                        down_name = name + '.docx'
                        st.download_button('保存为Word', texts, file_name=f'{down_name}')
    if add_selectbox == '图片采集':
        with st.sidebar:
            if st.button('获取随机图片'):
                img_list = get_img_url_list()
                imgs = random.choice(img_list)
        if imgs:
            st.image(f'{imgs}', caption='Sunrise by the mountains')
            img_info = down_img_content(imgs)
            btn = st.download_button(
                label="下载图片",
                data=img_info,
                file_name=f"flower.jpg",
                mime="image/jpg"
            )
        else:
            st.image(f'https://huamaobizhi.com/appApi/wallpaper/getImages_1_0/?pid=31161&resolution=1000w680h', caption='默认图片')
    if add_selectbox == 'Youtube视频采集':
        with st.sidebar:
            add_radio = st.text_area(label='请输入需要采集的链接:')
            button_code = st.button(':blue[采集]')
        if button_code:
            kids = re.findall('v=(.*)', add_radio)[0]
            vids = get_video_id(kids)
            if vids:
                video_url_list = get_info(kids, vids)
                if video_url_list:
                    for video in video_url_list:
                        st.header(f"画质:{video['视频画质']} 帧率:{video['视频帧率']}")
                        st.video(video['视频链接'])
                        st.write('右击视频保存')
                else:
                    st.write('视频采集失败')
            else:
                st.write('视频采集失败')
