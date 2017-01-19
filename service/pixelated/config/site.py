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

from twisted.web.server import Site, Request


class AddSecurityHeadersRequest(Request):
    CSP_HEADER_VALUES = "default-src 'self'; style-src 'self' 'unsafe-inline'"

    def process(self):
        self.setHeader('Content-Security-Policy', self.CSP_HEADER_VALUES)
        self.setHeader('X-Content-Security-Policy', self.CSP_HEADER_VALUES)
        self.setHeader('X-Webkit-CSP', self.CSP_HEADER_VALUES)
        self.setHeader('X-Frame-Options', 'SAMEORIGIN')
        self.setHeader('X-XSS-Protection', '1; mode=block')
        self.setHeader('X-Content-Type-Options', 'nosniff')

        if self.isSecure():
            self.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

        Request.process(self)


class PixelatedSite(Site):

    requestFactory = AddSecurityHeadersRequest

    @classmethod
    def enable_csp_requests(cls):
        cls.requestFactory = AddSecurityHeadersRequest

    @classmethod
    def disable_csp_requests(cls):
        cls.requestFactory = Site.requestFactory
