import threading


# 锁类，修改进程共享参数时防止冲突
class RWlock(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._extra = threading.Lock()
        self.write_num = 0

    def write_acquire(self):
        with self._extra:
            self.write_num += 1
            if self.write_num == 1:
                self._lock.acquire()
                # print('write_acquire')

    def write_release(self):
        with self._extra:
            self.write_num -= 1
            if self.write_num == 0:
                self._lock.release()
                # print('wirte_release')

    def read_acquire(self):
        self._lock.acquire()
        # print('read_acquire')

    def read_release(self):
        self._lock.release()
        # print('read_release')


Lock = RWlock()
