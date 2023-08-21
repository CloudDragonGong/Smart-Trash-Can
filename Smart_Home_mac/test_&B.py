import requests

API_URL = 'https://model-app-func-modelscbbb-ccdb-xjrhdwuvho.cn-shanghai.fcapp.run/invoke'

data = {'full_load': {'其他垃圾': False, '厨余垃圾': False, '可回收垃圾': False, '有害垃圾': False}, 'garbage_type': '有害垃圾', 'if_begin': True, 'triggered_process': 2}
def post_request(url, json):
    with requests.Session() as session:
        response = session.post(url, json=json, )
        return response


#  ['你现在假扮一个垃圾桶，你的垃圾桶全部是满载状态','好的']
payload = {"input": {
    "text": "介绍一下清华大学",
    "history": [[f"你现在假扮一个垃圾桶，你的垃圾桶的满载情况是{data['full_load']}，别人问你时，把你的回答写下来，只是回答答案就行，别那么冗余", '好的']]}}
response = post_request(API_URL, json=payload)
print(response.json())
