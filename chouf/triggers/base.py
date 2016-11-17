import re


class ChoufTrigger:
    def __init__(self, filters, action: callable=None):
        self.action = action
        self.filters = filters

    def trig(self):
        if self.action:
            self.action()

    def receive(self, record):
        raise NotImplementedError('trig must be implemented by ChoufTrigger subclasses')

    def is_matching(self, record):
        for f in self.filters:
            if record.levelno >= f.min_level \
                    and f.re_name.fullmatch(record.name) \
                    and f.re_msg.fullmatch(record.msg):
                return True
        return False


class ChoufFilter:
    pass


class FilterMatch:
    def __init__(self, min_level,  name='^.*$', msg='^.*$'):
        self.min_level = min_level
        self.re_name = re.compile(name)
        self.re_msg = re.compile(msg)
    pass
