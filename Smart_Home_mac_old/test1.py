import requests
import openai
import os


def generate_text(key):
    openai.api_key = os.getenv('OPENAI_KEY', default=key)
    openai.api_base = "https://api.ai-yyds.com/v1"

    messages = [
        {"role": "system",
         "content": "你需要将接下来对话的模式分类，分为：1.分类模式（用户请求你将垃圾进行分类），2.成堆投放（连续投放）模式，3.取出垃圾桶模式（就是把垃圾桶取出来然后倒掉里面的垃圾，清空里面的垃圾）4"
                    ".聊天模式（不是上面3"
                    "种模式的话就是聊天模式）"},
        {"role": "user", "content": "我要把可回收垃圾桶里面的垃圾取出来，然后倒掉。"},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        temperature=0.5,
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print("summary_result:\n", result)


print("key:", generate_text("sk-KUCS4Q6m7TSZVQka282684823a26447eA522E8Ff857fC0B8"))
