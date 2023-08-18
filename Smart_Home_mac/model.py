import requests

API_URL = 'https://model-app-func-modelscbbb-ccdb-xjrhdwuvho.cn-shanghai.fcapp.run/invoke'


class Model:
    def __init__(self, prompt):
        self.history = [
            [prompt,'好的']
        ]

    def response(self, text):
        payload = {"input": {"text": text, "history": self.history}}
        with requests.Session() as session:
            response_dict = session.post(API_URL, json=payload, ).json()
        response_text = response_dict['Data']['text']
        return response_text


if __name__ == '__main__':
    data = {
        'full_load': [True, True, True, True]
    }
    prompt = f"""
    你现在扮演一个智能垃圾桶的语音助手/
    现在垃圾桶的满载情况是{data['full_load']}/
    待会有人问你问题，你就回答的简单一点，简短，快速
    """
    model = Model(prompt)
    res = model.response('垃圾桶还能放垃圾吗？')
    print(res)
