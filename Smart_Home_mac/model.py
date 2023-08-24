import openai
import os

API_KEY = "sk-KUCS4Q6m7TSZVQka282684823a26447eA522E8Ff857fC0B8"


class Model:
    def __init__(self, prompt=None):
        openai.api_key = os.getenv('OPENAI_KEY', default=API_KEY)
        openai.api_base = "https://api.ai-yyds.com/v1"

        self.messages = []
        if prompt is None:
            self.messages.append({"role": "system", "content": '你是一个智能垃圾桶的语音助手'})
        else:
            self.messages.append({"role": "system", "content": prompt})

    def response(self, text):
        while True:
            try:
                self.messages.append({"role": "user", "content": text})
                response = openai.ChatCompletion.create(
                    model="gpt-4-0613",
                    messages=self.messages,
                    temperature=0.5,
                )
                result = ''
                for choice in response.choices:
                    result += choice.message.content
                print(result)
                return result
            except Exception:
                print('response error  continue')
                pass

    def add_system_prompt(self, prompt):
        self.messages.append({"role": "system", "content": prompt})


if __name__ == '__main__':
    data = {
        'full_load': [True, True, True, True]
    }
    model = Model(data)
    model.add_system_prompt(
        "你需要将接下来对话的模式分类，分为：1.分类模式（用户请求你将垃圾进行分类，并且还要投放），2.成堆投放（连续投放）模式("
        "特点投放很多垃圾，连续成堆投放），3.取出垃圾桶模式（就是把垃圾桶取出来然后倒掉里面的垃圾，清空里面的垃圾）4"
        ".聊天模式（不是上面3"
        "种模式的话就是聊天模式）")
    res = model.response('我要把可回收垃圾桶里面的垃圾取出来，然后倒掉。')
    print(res)
