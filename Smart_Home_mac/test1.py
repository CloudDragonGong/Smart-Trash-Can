keywords = ["分类模式", "成堆投放模式", "倒垃圾模式"]
response_str = "'倒垃圾模式'"
print("倒垃圾模式" in response_str)
print((keyword in response_str for keyword in keywords))
if any(keyword in response_str for keyword in keywords):
    print('ok')
