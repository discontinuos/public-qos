from multiprocessing import RawValue, Lock

class Counter(object):
    def __init__(self, value=0):
        # RawValue because we don't need it to create a Lock:
        self.val = RawValue('i', value)
        self.lock = Lock()

    def Increment(self, value=1):
        with self.lock:
            self.val.value += value

    def getValue(self):
        with self.lock:
            return self.val.value

    Value = property(getValue)
