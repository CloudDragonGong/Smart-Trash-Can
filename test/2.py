from multiprocessing import Process,Queue
import multiprocessing
import time
q = Queue(1)
information ={
    '1' : 1 ,
    '2' : 2 ,
    '3' : 3 ,
}

def main_run(information,q):
    print('main_run begin')
    while True:
        information['1']+=1
        information['2']+=1
        information['3']+=1
        q.put(information)
        # print("___________________________")
        print('\n\n\n the truth is :\n'+str(information)+'\n\n\n')
        # print("-----------------------------")
        time.sleep(0.5)

def return_information(information):
    return information


def subprocess(information):
    while(True):
        time.sleep(0.5)
        print('the subprocess received :')
        print(information)

def subprocess2(q):
    while(True):
        time.sleep(0.5)
        print('the subprocess received :')
        print(q.get())

if __name__ == '__main__':
    multiprocessing.freeze_support()        
    # sub_process = Process(target=subprocess,args=(return_information(information=information),))
    # sub_process.start()
    sub_process = Process(target=subprocess2,args=(q,))
    sub_process.start()
    main_run(information=information,q=q)