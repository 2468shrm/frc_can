
class CIRCULAR_BUFFER:
    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.lst = [0] * maxlen
        self.lst_index = 0

    def add(self, val):
        self.lst[self.lst_index] = val
        self.lst_index += 1
        if self.lst_index == self.maxlen:
            self.lst_index = 0

    def average(self):
        _total = 0
        for i in range(self.maxlen):
            _total += self.lst[i]
        return _total / self.maxlen
# Write your code here :-)
