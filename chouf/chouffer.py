from logging import Handler


class ChoufHandler(Handler):
    def __init__(self, triggers):
        Handler.__init__(self)
        self.triggers = triggers

    def emit(self, record):
        for trigger in self.triggers:
            trigger.receive(record)
