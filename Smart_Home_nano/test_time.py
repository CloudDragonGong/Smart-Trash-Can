def a(num):
    if num % 100 == 0:
        return True
    else:
        print('no no no ')

num = 0
while a(num):
    print('ok')
    num = num+ 1
