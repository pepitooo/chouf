import threading
import time

from chouf.triggers.base import ChoufTrigger


def default_key_gen(record):
    return '{}:{}:{}'.format(record.name, record.funcName, str(record.lineno))


class RepeatedRecordTrigger(ChoufTrigger):
    def __init__(self, times=1, period_s=0, filters=None, action: callable = None,
                 key_generator: callable = default_key_gen):
        if filters is None:
            filters = []
        super().__init__(filters, action)
        self.times = times
        self.period_s = period_s
        self.history = []
        self.key_gen = key_generator

    def receive(self, record):
        if self.is_matching(record):
            if self.is_ready_to_fire(record):
                t = threading.Thread(target=lambda: self.trig())
                t.start()

    def is_ready_to_fire(self, record, current_time=None):
        if self.period_s <= 0 or self.times <= 1:
            return True

        key = self.key_gen(record)
        ct = current_time or time.time()
        # remove old records
        consider_as_old = ct - self.period_s
        self.history = [el for el in self.history if el['ct'] > consider_as_old]

        self.history.append(dict(ct=ct, key=key))
        return len([el for el in self.history if el['key'] == key]) >= self.times


