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

import os
from distutils.spawn import find_executable


def discover_gpg_binary():
    path = find_executable('gpg')
    if path is None:
        raise Exception('Did not find a gpg executable!')

    if os.path.islink(path):
        path = os.path.realpath(path)

    return path


SYSTEM_CA_BUNDLE = True
leap_home = os.path.expanduser('~/.leap/')
gpg_binary = discover_gpg_binary()


def set_leap_home(new_home):
    leap_home = new_home


def set_gpg_binary(new_binary):
    gpg_binary = binary
