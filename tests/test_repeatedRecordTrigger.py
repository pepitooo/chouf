import logging
import logging.config
import queue
import time
import sys

from unittest import TestCase

from chouf.chouffer import ChoufHandler
from chouf.triggers.base import FilterMatch
from chouf.triggers.repeat import RepeatedRecordTrigger


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s.%(msecs)03d %(levelname)s %(name)s:%(filename)s:%(lineno)d %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
logging.config.dictConfig(LOGGING)

_logger = logging.getLogger(__name__)

stack_msg = queue.Queue()

action_name = 'action_name_secure'


class TestRepeatedRecordTrigger(TestCase):
    def setUp(self):
        self.f = FilterMatch(min_level=logging.WARNING, name='^[a-zA-Z]*$', msg='^[a-zA-Z0-9]*$')

    def test_matching_level_name_msg(self):
        rrt = RepeatedRecordTrigger(1, 0, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.WARNING, pathname='', lineno=0,
                                   msg='ok', args='', exc_info='')
        assert rrt.is_matching(record)

    def test_not_matching_level(self):
        rrt = RepeatedRecordTrigger(1, 0, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.INFO, pathname='', lineno=0,
                                   msg='ok', args='', exc_info='')
        assert not rrt.is_matching(record)

    def test_not_matching_name(self):
        rrt = RepeatedRecordTrigger(1, 0, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='not_ok', level=logging.ERROR, pathname='', lineno=0,
                                   msg='ok', args='', exc_info='')
        assert not rrt.is_matching(record)

    def test_not_matching_msg(self):
        rrt = RepeatedRecordTrigger(1, 0, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.ERROR, pathname='', lineno=0,
                                   msg='not_ok', args='', exc_info='')
        assert not rrt.is_matching(record)

    def test_ready_to_fire_after_once(self):
        rrt = RepeatedRecordTrigger(1, 10, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.ERROR, pathname='', lineno=0,
                                   msg='not_ok', args='', exc_info='')

        assert rrt.is_ready_to_fire(record)

        rrt = RepeatedRecordTrigger(10, 0, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.ERROR, pathname='', lineno=0,
                                   msg='not_ok', args='', exc_info='')

        assert rrt.is_ready_to_fire(record)

    def test_ready_to_fire_discard_old_record(self):
        rrt = RepeatedRecordTrigger(3, 10, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.ERROR, pathname='', lineno=0,
                                   msg='not_ok', args='', exc_info='')

        ct = time.time()

        assert not rrt.is_ready_to_fire(record, ct - 15)
        assert not rrt.is_ready_to_fire(record, ct - 14)
        assert not rrt.is_ready_to_fire(record, ct - 1)
        assert not rrt.is_ready_to_fire(record, ct - 0)
        assert rrt.is_ready_to_fire(record, ct + 1)

    def test_ready_to_fire_ok(self):
        rrt = RepeatedRecordTrigger(3, 10, [self.f], lambda: print('ok'))
        record = logging.LogRecord(name='ok', level=logging.ERROR, pathname='', lineno=0,
                                   msg='not_ok', args='', exc_info='')

        assert not rrt.is_ready_to_fire(record)
        assert not rrt.is_ready_to_fire(record)
        assert rrt.is_ready_to_fire(record)


def action():
    stack_msg.put(action_name)


def key_gen(record):
    return record.name + record.funcName


class TestLoggerHandler(TestCase):
    def setUp(self):
        pass

    def test_received_action(self):
        f = FilterMatch(min_level=logging.WARNING, name='^[a-zA-Z\._]*repeatedRecordTrigger$', msg='^.*$')
        rrt = RepeatedRecordTrigger(times=1, period_s=0, filters=[f], action=lambda: action())
        ch = ChoufHandler(triggers=[rrt])
        logging.root.addHandler(ch)

        assert stack_msg.empty()
        _logger.debug("ok")
        assert stack_msg.empty()

        _logger.info("ok")
        assert stack_msg.empty()

        _logger.warn("ok")
        assert action_name == stack_msg.get()

        _logger.error("ok")
        assert action_name == stack_msg.get()

        _logger.critical("ok")
        assert action_name == stack_msg.get()
        assert stack_msg.empty()
        logging.root.removeHandler(ch)

    def test_action_come_after_x_records(self):
        f = FilterMatch(min_level=logging.WARNING, name='^[a-zA-Z\._]*repeatedRecordTrigger$', msg='^.*$')
        rrt = RepeatedRecordTrigger(times=4, period_s=10, filters=[f], action=lambda: action(), key_generator=key_gen)
        ch = ChoufHandler(triggers=[rrt])
        logging.root.addHandler(ch)

        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert action_name == stack_msg.get(block=False)
        assert stack_msg.empty()
        logging.root.removeHandler(ch)

    def test_action_come_after_x_records_by_reset_by_time(self):
        f = FilterMatch(min_level=logging.WARNING, name='^[a-zA-Z\._]*repeatedRecordTrigger$', msg='^.*$')
        rrt = RepeatedRecordTrigger(times=4, period_s=.1, filters=[f], action=lambda: action(), key_generator=key_gen)
        ch = ChoufHandler(triggers=[rrt])
        logging.root.addHandler(ch)

        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert action_name == stack_msg.get()
        assert stack_msg.empty()

        time.sleep(.3)
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert stack_msg.empty()
        _logger.warn("ok")
        assert action_name == stack_msg.get()
        assert stack_msg.empty()

        logging.root.removeHandler(ch)
