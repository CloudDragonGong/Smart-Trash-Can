from threading import Thread
import time

information ={
    '1' : 1 ,
    '2' : 2 ,
    '3' : 3 ,
}

def main_run(information):
    print('main_run begin')
    while True:
        information['1'] += 1
        information['2'] += 1
        information['3'] += 1
        print('\n\n\n the truth is :\n' + str(information) + '\n\n\n')
        time.sleep(0.5)

def return_information(information):
    return information

def subprocess(information):
    while True:
        time.sleep(0.5)
        print('the subprocess received :')
        print(information)

if __name__ == '__main__':
    sub_thread = Thread(target=subprocess, args=(return_information(information=information),))
    sub_thread.start()
    main_run(information=information)
