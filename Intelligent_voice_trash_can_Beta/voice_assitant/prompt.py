import openai
import os

class ChatGPT():
    def __init__(self,api_key,information):
        self.api_key = api_key
        self.information = information
        openai.api_key = self.api_key
        

    def get_completion(self,prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]
    
    def get_completion_from_messages(self,messages, model="gpt-3.5-turbo", temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature, # this is the degree of randomness of the model's output
        )
        #print(str(response.choices[0].message))
        return response.choices[0].message["content"]
    
    def get_response(self,text):

        # self.text = text
        # self.prompt = f"""
        #     你现在是一个智能垃圾桶的语音助手，你要按照下面的顺序来思考，并且做出你的最终回答\
        #     - 分类对方问的是哪方面,主要有两个方面，一个是 询问垃圾桶的分类方式，一个是询问垃圾桶的状况（有多少垃圾）\
        #     - 依据上面的分类结果，如果是问垃圾有哪些分类方式的这方面，你就用下面的格式回答本垃圾桶的四个分类：1.有害垃圾，2.厨余垃圾，3.可回收垃圾，4.其他垃圾，格式为\
        #     “有害垃圾，例如电池...\
        #     厨余垃圾，例如西瓜...\
        #     可回收垃圾，例如...\
        #     其他垃圾例如...\
        #     ”\
        #     注意，上面省略号的部分，你可以多加几种垃圾进去，不限于上面的电池啊啥的\
        #     回答完之后就直接结束。\
        #     - 依据上面的分类结果，如果是问四个垃圾桶的状况，比如“垃圾桶有多少垃圾啊？”“垃圾桶的状态是怎么样的呢”这一类问题\
        #     按照下面的格式回答：\
        #     “\
        #         - 有害垃圾有'''{self.information['hazardous waste']}'''个\
        #         - 厨余垃圾有'''{self.information['Kitchen waste']}'''个\
        #         - 可回收垃圾有'''{self.information['recyclable trash']}'''个\
        #         - 其他垃圾有'''{self.information['other garbage']}'''个\
        #     ”\
        #     同样，回答完这个后就不用回答了。\
        #     如果，他问了上面的两个方面的问题，你就把上面两个方面的内容都回答，这样就行了\
        #     如果，他问的问题不属于上面任何一个方面，你就回答“抱歉，作为智能垃圾桶的语音助手，我只能回答有关垃圾桶的分类方式和垃圾桶的状况的问题，其他的我无能为力”\
        #     好的，他现在正在问下面的问题'''{text}'''\
        #     """ 
        # return self.get_completion(self.prompt)
        prompt = "你好主任，我是智能垃圾桶的语音助手，有什么垃圾桶的状况或者是其他知识需要问我的？"
        context = [{'role':'system','content':f""" 你是一个说中文的智能垃圾桶语音聊天机器人，这个垃圾桶的功能是当用户投放垃圾到投放口，你能自动识别，并且分成四个类别，垃圾桶有四个，分别为有害垃圾垃圾桶，厨余垃圾垃圾桶，可回收垃圾垃圾桶，其他垃圾垃圾桶，\
            现在,有害垃圾有'''{self.information['hazardous waste']}'''个'\
            厨余垃圾有'''{self.information['Kitchen waste']}'''个\
            可回收垃圾有'''{self.information['recyclable trash']}'''个\
            其他垃圾有'''{self.information['other garbage']}'''个 \
            满载情况为'''{self.information['fullLoadGarbage']}''' (如果是none，那就是没有满载，如果不是none，那就是满载了)"""}
            ,{'role':'assistant','content':prompt}]
        self.text=text
        context.append({'role':'user','content':text})
        return self.get_completion_from_messages(context,temperature=1)


if __name__ == '__main__':
    information = {'hazardous waste':1,'Kitchen waste':2,'recyclable trash':3,'other garbage':4,'fullLoadGarbage':True}
    gpt = ChatGPT("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",information=information)
    text = '这个垃圾桶的可回收垃圾有几个？'
    print(gpt.get_response(text))
