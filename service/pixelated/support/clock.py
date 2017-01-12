from datetime import datetime
from os.path import expanduser


class Clock():

    def __init__(self, label, user=None):
        self.start = datetime.now()
        self.label = label
        self.user = user

    def stop(self, fresh=False, user=None):
        end = datetime.now()
        with open(expanduser('~/MetricsTime'), 'a') as f:
            flag = ' fresh-account' if fresh else ''
            f.write('{} {:.5f} {} {}\n'.format((self.user or user or 'Unknown'), (end - self.start).total_seconds(), self.label, flag))
