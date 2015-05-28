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
import base64
import logging
import quopri
import re

from twisted.internet import defer

from pixelated.adapter.model.mail import PixelatedMail
from pixelated.adapter.soledad.soledad_facade_mixin import SoledadDbFacadeMixin


logger = logging.getLogger(__name__)


class SoledadReaderMixin(SoledadDbFacadeMixin, object):
    """
    Explaining the documents:

    - fdoc: Flags document, these documents are the basis of the mail and have
    the first mail identifier, the c-hash (or content hash)
    - hdoc: Headers document, these are identified by the c-hash and contain the
    headers of a mail, they also have a list of p-hashes (body identifier)
    - bdoc: Body documents, each mail part is a body document, they have a mime
    type and a content basically and are identified by a p-hash
    """
    @defer.inlineCallbacks
    def all_mails(self):
        deferred = self.get_all_flags()
        deferred.addCallback(self._build_fdocs_chashes)
        deferred.addCallback(self._build_fdocs_hdocs)
        deferred.addCallback(self._build_fdocs_hdocs_phashes)
        deferred.addCallback(self._build_fdocs_hdocs_bdocs)
        deferred.addCallback(self._build_mails)
        mails = yield deferred
        defer.returnValue(mails)

    def _build_fdocs_chashes(self, fdocs):
        return [(fdoc, fdoc.content['chash']) for fdoc in fdocs]

    def _build_fdocs_hdocs(self, fdocs_chashes):
        if not fdocs_chashes:
            return []

        deferred_list = defer.DeferredList([self.get_header_by_chash(chash) for _, chash in fdocs_chashes])

        fdocs, _ = zip(*fdocs_chashes)

        deferred_list.addCallback(partial(self._fdocs_hdocs, fdocs))
        return deferred_list

    def _build_fdocs_hdocs_phashes(self, fdocs_hdocs):
        return [(fdoc, hdoc, hdoc.content.get('body')) for fdoc, hdoc in fdocs_hdocs]

    def _build_fdocs_hdocs_bdocs(self, fdocs_hdocs_phashes):
        if not fdocs_hdocs_phashes:
            return []

        deferred_list = defer.DeferredList([self.get_content_by_phash(phash) for _, _, phash in fdocs_hdocs_phashes])

        fdocs, hdocs, _ = zip(*fdocs_chashes)

        deferred_list.addCallback(partial(self._fdocs_hdocs_bdocs, fdocs, hdocs))
        return deferred_list

    def _build_mails(self, fdocs_hdocs_bdocs):
        if not fdocs_hdocs_bdocs:
            return []

        return [PixelatedMail.from_soledad(fdoc, hdoc, bdoc, soledad_querier=self) for fdoc, hdoc, bdoc in fdocs_hdocs_bdocs]

    def _fdocs_hdocs(self, fdocs, hdocs):
        return zip(fdocs, hdocs)

    def _fdocs_hdocs_bdocs(self, fdocs, hdocs, bdocs):
        return zip(fdocs, hdocs, bdocs)

    def mail_exists(self, ident):
        return self.get_flags_by_chash(ident)

    def mail(self, ident):
        fdoc = self.get_flags_by_chash(ident)
        hdoc = self.get_header_by_chash(ident)
        bdoc = self.get_content_by_phash(hdoc.content['body'])
        parts = self._extract_parts(hdoc.content)

        return PixelatedMail.from_soledad(fdoc, hdoc, bdoc, parts=parts, soledad_querier=self)

    def mails(self, idents):
        fdocs_chash = [(self.get_flags_by_chash(ident), ident) for ident in
                       idents]
        fdocs_chash = [(result, ident) for result, ident in fdocs_chash if result]
        return self._build_mails_from_fdocs(fdocs_chash)

    def attachment(self, attachment_ident, encoding):
        bdoc = self.get_content_by_phash(attachment_ident)
        return {'content': self._try_decode(bdoc.content['raw'], encoding),
                'content-type': bdoc.content['content-type']}

    def _try_decode(self, raw, encoding):
        encoding = encoding.lower()
        if encoding == 'base64':
            return base64.decodestring(raw)
        elif encoding == 'quoted-printable':
            return quopri.decodestring(raw)
        else:
            return str(raw)

    def _extract_parts(self, hdoc, parts=None):
        if not parts:
            parts = {'alternatives': [], 'attachments': []}

        if hdoc['multi']:
            for part_key in hdoc.get('part_map', {}).keys():
                self._extract_parts(hdoc['part_map'][part_key], parts)
        else:
            headers_dict = {elem[0]: elem[1] for elem in hdoc.get('headers', [])}
            if 'attachment' in headers_dict.get('Content-Disposition', ''):
                parts['attachments'].append(self._extract_attachment(hdoc, headers_dict))
            else:
                parts['alternatives'].append(self._extract_alternative(hdoc, headers_dict))
        return parts

    def _extract_alternative(self, hdoc, headers_dict):
        bdoc = self.get_content_by_phash(hdoc['phash'])

        if bdoc is None:
            logger.warning("No BDOC content found for message!!!")
            raw_content = ""
        else:
            raw_content = bdoc.content['raw']

        return {'headers': headers_dict, 'content': raw_content}

    def _extract_attachment(self, hdoc, headers_dict):
        content_disposition = headers_dict['Content-Disposition']
        match = re.compile('.*name=\"(.*)\".*').search(content_disposition)
        filename = ''
        if match:
            filename = match.group(1)
        return {'headers': headers_dict, 'ident': hdoc['phash'], 'name': filename}
