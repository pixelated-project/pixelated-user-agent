#!/usr/bin/env python
#
# Copyright (c) 2014 ThoughtWorks, Inc.
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

from setuptools import setup

import datetime
import time

now = datetime.datetime.now()
timestamp = time.strftime('%Y%m%d', now.timetuple())

setup(name='pixelated-www',
      version='0.1.%s' % timestamp,
      description='Pixelated User Agent UI',
      author='Thoughtworks',
      author_email='pixelated-team@thoughtworks.com',
      url='http://pixelated-project.github.io',
      packages=['pixelated_www'],
      package_data={
          '': ['protected/*',
               'protected/css/*',
               'protected/fonts/*',
               'public/*',
               'public/fonts/*',
               'public/locales/en_US/*',
               'public/locales/pt_BR/*',
               'public/locales/sv_SE/*']},
      zip_safe=False)
