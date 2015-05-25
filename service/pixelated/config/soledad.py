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

from pixelated.bitmask_libraries.session import open as open_leap_session
from pixelated.adapter.soledad.soledad_querier import SoledadQuerier


def init_soledad_and_user_key(app, leap_home):
    leap_session = open_leap_session(app['LEAP_USERNAME'],
                                     app['LEAP_PASSWORD'],
                                     app['LEAP_SERVER_NAME'],
                                     leap_home)
    soledad = leap_session.soledad_session.soledad
    leap_session.nicknym.generate_openpgp_key()

    soledad.sync(defer_decryption=False)

    def get_leap_session(_):
        return leap_session

    querier = SoledadQuerier(soledad)
    deferred = querier.initialize_store(soledad)
    deferred.addCallback(get_leap_session)
    return deferred
