import streamlit as st
import requests
import base64
import json
from PIL import Image


def parse_img(path):
    """
    解析图片
    :param path:
    :return:
    """
    with open(f"{path}", "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
        return image_data


def google_gemini_pro_vision(image_data, question):
    """
    调用谷歌双子座的填写图片模型
    :return:
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
      "contents": [
          {
              "parts": [
                  {
                      "inlineData": {
                          "mimeType": "image/jpeg",
                          "data": image_data
                      }
                  },
                  {
                      "text": f"{question}"
                  }
              ]
          }
      ],
      "generationConfig": {
          "temperature": 0.4,
          "topK": 32,
          "topP": 1,
          "maxOutputTokens": 4096,
          "stopSequences": []
      },
      "safetySettings": [
          {
              "category": "HARM_CATEGORY_HARASSMENT",
              "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
              "category": "HARM_CATEGORY_HATE_SPEECH",
              "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
              "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
              "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
              "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          }
      ]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key=AIzaSyCYwX9oNzx88dd5gyLaN9lXRC5ppKxNQ5M"  # 记得修改key
    response = requests.post(url, headers=headers, data=json.dumps(data)).json()
    response_json = response["candidates"][0]["content"]["parts"][0]["text"]
    print(response_json)
    return response_json


def gemini_pro(question):
    """
    调用谷歌双子座模型
    :param question:问题
    :return: 答案
    """
    headers = {
        "Content-Type": "application/json"
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    params = {
        "key": "AIzaSyCYwX9oNzx88dd5gyLaN9lXRC5ppKxNQ5M"
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
        print(info)
        return info
    except Exception as e:
        print(e)



class gemini:

    def __init__(self):
        self.function_type = None  # 功能类别
        self.selectbox_options = (
            "AI_PRO_TXT",
            "AI_PRO_IMG",
        )


    def streamlit_selectbox(self):
        """
        侧边栏初始化
        :return:
        """
        tool_selectbox = st.sidebar.selectbox(
            label="AI切换",
            options=self.selectbox_options
        )
        return tool_selectbox


    def ai_pro_txt(self):
        """
        文本问答功能
        """
        if self.function_type == self.selectbox_options[0]:
            st.title('文本识别问答')
            with st.sidebar:
                st.caption(":blue[介绍:]")
                st.caption(":blue[本功能调用谷歌文本大模型,只需要填写问题即可.]")
            prompt = st.chat_input("请输入问题:")
            if prompt:
                with st.chat_message("user"):
                    st.write(f"问题：{prompt}")
                with st.spinner('正在编写答案'):
                    info = gemini_pro(prompt)
                with st.chat_message("👋"):
                    st.write(f"{info}")


    def ai_pro_img(self):
        """
        图片识别解析问答功能
        :return:
        """
        if self.function_type == self.selectbox_options[1]:
            st.title('图片识别问答')
            with st.sidebar:
                st.caption(":blue[介绍:]")
                st.caption(":blue[本功能调用谷歌图片解析大模型,必须先上传图片,显示图片上传成功后才能开启问答功能！.]")
                image_file = st.file_uploader("上传图片", type=["jpg", "png", "jpeg"])
                code = 0
                if image_file:
                    image_data = image_file.read()
                    base64_string = base64.b64encode(image_data).decode("utf-8")
                    image = Image.open(image_file)
                    st.image(image, caption="上传的图片")
                    st.success('图片上传成功')
                    code = 1
            if code:
                prompt = st.chat_input("请输入问题:")
                if prompt:
                    with st.chat_message("user"):
                        st.write(f"问题：{prompt}")
                    with st.spinner('正在编写答案'):
                        info = google_gemini_pro_vision(base64_string, prompt)
                    with st.chat_message("👋"):
                        st.write(f"{info}")


    def streamlit_function(self):
        """
        侧边栏执行功能
        :return:
        """
        self.function_type = self.streamlit_selectbox()
        self.ai_pro_txt()
        self.ai_pro_img()


if __name__ == '__main__':
    gemini = gemini()
    gemini.streamlit_function()
