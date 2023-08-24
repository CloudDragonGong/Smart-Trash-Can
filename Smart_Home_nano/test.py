from  multiprocessing  import Queue
q = Queue(1)

if q is None:
    print('ok')
print('no')