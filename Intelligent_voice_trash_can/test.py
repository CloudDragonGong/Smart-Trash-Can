import os



# 然后尝试使用相对路径访问
voice_path = './voice'
if os.path.exists(voice_path):
    print("路径存在")
else:
    print("路径不存在")
