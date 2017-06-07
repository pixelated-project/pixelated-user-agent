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

import datetime
import os
from setuptools import setup
import time

now = datetime.datetime.now()
timestamp = time.strftime('%Y%m%d', now.timetuple())


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pixelated-user-agent',
      version='0.1.%s' % timestamp,
      description='API to serve the pixelated front-end requests',
      long_description=read('README.md'),
      author='Thoughtworks',
      author_email='pixelated-team@thoughtworks.com',
      url='https://github.com/pixelated',
      packages=[
          'pixelated',
          'pixelated.adapter',
          'pixelated.adapter.listeners',
          'pixelated.adapter.model',
          'pixelated.adapter.search',
          'pixelated.adapter.services',
          'pixelated.adapter.mailstore',
          'pixelated.adapter.mailstore.maintenance',
          'pixelated.bitmask_libraries',
          'pixelated.config',
          'pixelated.assets',
          'pixelated.certificates',
          'pixelated.support',
          'pixelated.resources',
          'pixelated.extensions'
      ],
      install_requires=[],
      entry_points={
          'console_scripts': [
              'pixelated-user-agent = pixelated.application:initialize',
              'pixelated-maintenance = pixelated.maintenance:initialize',
              'pixelated-register = pixelated.register:initialize'
          ]
      },
      include_package_data=True)
