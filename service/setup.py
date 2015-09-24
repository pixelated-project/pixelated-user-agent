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
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pixelated-user-agent',
      version='0.1',
      description='API to serve the pixelated front-end requests',
      long_description=read('README.md'),
      author='Thoughtworks',
      author_email='pixelated-team@thoughtworks.com',
      url='http://pixelated-project.github.io',
      packages=[
          'pixelated',
          'pixelated.adapter',
          'pixelated.adapter.listeners',
          'pixelated.adapter.model',
          'pixelated.adapter.mailstore',
          'pixelated.adapter.search',
          'pixelated.adapter.services',
          'pixelated.bitmask_libraries',
          'pixelated.config',
          'pixelated.assets',
          'pixelated.certificates',
          'pixelated.support',
          'pixelated.resources',
          'pixelated.extensions'
      ],
      install_requires=[
           'pyasn1==0.1.8',
           'requests==2.0.0',
           'srp==1.0.4',
           'dirspec==4.2.0',
           'u1db==13.09',
#           'leap.mail>=0.4.0',  # not in a stable repo yet, see requirements.txt
           'leap.auth==0.1.2',
           'whoosh==2.5.7'
      ],
      entry_points={
          'console_scripts': [
              'pixelated-user-agent = pixelated.application:initialize',
              'pixelated-maintenance = pixelated.maintenance:initialize',
              'pixelated-register = pixelated.register:initialize'
          ]
      },
      include_package_data=True
)
