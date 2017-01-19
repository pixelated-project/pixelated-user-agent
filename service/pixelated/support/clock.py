#
# Copyright (c) 2015 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.

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
