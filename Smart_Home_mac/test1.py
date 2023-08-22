import queue

q = queue.Queue(1)
q.put(0)
def a ():
    try:
        q.put_nowait(0)
    except queue.Full:
        print('o')
def b():
    a()
    print('okk')
b()
print('okkk')