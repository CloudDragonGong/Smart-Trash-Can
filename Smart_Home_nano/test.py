from  threading import Thread
import time
data={'should_stop':False}

def func_1(data):
    a = 2
    while (not data['should_stop'] )and (a>0):
        time.sleep(1)
        a=a-1
    data['should_stop']=True
    print(f'func1 is finished')

def func_2(data):
    a = 10
    while (not data['should_stop']) and (a > 0):
        time.sleep(1)
        a = a - 1
    data['should_stop'] = True
    print(f'func2 is finished')


thread1 = Thread(target=func_1,args=(data,))
thread2 = Thread(target=func_2,args=(data,))
start_time = time.time()

thread1.start()
thread2.start()

thread1.join()
thread2.join()
end_time = time.time()
elapsed_time = end_time-start_time
print(f"{data['should_stop']}, and the time is {elapsed_time:.2f}秒")
