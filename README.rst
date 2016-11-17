=====
Chouf
=====

Chouf is used to design a guy who spy police and whistle when they arrive inside a quarter where drug dealer are doing
business.


Description
===========

This module is Logging handler how do custom action

I was looking for a light framework able to act when something wrong arrive on execution.
I didn't need a big solution.

For my project, when I was loosing USB connection I wanted to act quickly.

If a log record CRITICAL arrive 2 times in less than 2 seconds, It's easy to act with the lib.

Let me show you.


.. code:: python
from chouf.chouffer import ChoufHandler
from chouf.triggers.base import FilterMatch
from chouf.triggers.repeat import RepeatedRecordTrigger
    
def action():
   print('Action fired')

f = FilterMatch(min_level=logging.CRITICAL, name='^.*$', msg='^.*$')
rrt = RepeatedRecordTrigger(times=10, period_s=5, filters=[f], action=lambda: action())
ch = ChoufHandler(triggers=[rrt])
logging.root.addHandler(ch)



With this piece of code If a critical log record arrive 10 times in 5 second action will be executed

Of course you can define many triggers, and filter you want.