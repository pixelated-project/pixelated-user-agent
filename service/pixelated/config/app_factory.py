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
import sys

from OpenSSL import SSL
from OpenSSL import crypto
from twisted.internet import reactor
from twisted.internet import ssl
from pixelated.resources.root_resource import RootResource
from twisted.web import resource
from twisted.web.util import redirectTo
from pixelated.adapter.services.mail_service import MailService
from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.services.mail_sender import MailSender
from pixelated.adapter.services.mailboxes import Mailboxes
from pixelated.adapter.soledad.soledad_querier import SoledadQuerier
from pixelated.adapter.search import SearchEngine
from pixelated.adapter.services.draft_service import DraftService
from pixelated.adapter.listeners.mailbox_indexer_listener import MailboxIndexerListener
import pixelated.bitmask_libraries.session as LeapSession
from pixelated.bitmask_libraries.leap_srp import LeapAuthException
from requests.exceptions import ConnectionError
from leap.common.events import (
    register,
    unregister,
    events_pb2 as proto
)
from twisted.web.server import Site
from .welcome_mail import check_welcome_mail_wrapper

CREATE_KEYS_IF_KEYS_DONT_EXISTS_CALLBACK = 12345


def init_index_and_remove_dupes(querier, search_engine, mail_service):
    def wrapper(*args, **kwargs):
        querier.remove_duplicates()
        search_engine.index_mails(mails=mail_service.all_mails(),
                                  callback=querier.mark_all_as_not_recent)

    return wrapper


def update_info_sync_and_index_partial(sync_info_controller, search_engine, mail_service):
    def wrapper(soledad_sync_status):
        sync_info_controller.set_sync_info(soledad_sync_status)
        search_engine.index_mails(mails=mail_service.all_mails())

    return wrapper


def init_leap_session(app, leap_home):
    try:
        leap_session = LeapSession.open(app.config['LEAP_USERNAME'],
                                        app.config['LEAP_PASSWORD'],
                                        app.config['LEAP_SERVER_NAME'],
                                        leap_home=leap_home)
    except ConnectionError, error:
        print("Can't connect to the requested provider", error)
        reactor.stop()
        sys.exit(1)
    except LeapAuthException, e:
        print("Couldn't authenticate with the credentials provided %s" % e.message)
        reactor.stop()
        sys.exit(1)
    return leap_session


def look_for_user_key_and_create_if_cant_find(leap_session):
    def wrapper(*args, **kwargs):
        leap_session.nicknym.generate_openpgp_key()
        unregister(proto.SOLEDAD_DONE_DATA_SYNC, uid=CREATE_KEYS_IF_KEYS_DONT_EXISTS_CALLBACK)

    return wrapper


def stop_incoming_mail_fetcher(reactor_stop_function, leap_session):
    def wrapper():
        leap_session.stop_background_jobs()
        reactor.threadpool.stop()
        reactor_stop_function()
    return wrapper


def init_app(app, leap_home, leap_session):
    leap_session.start_background_jobs()
    keymanager = leap_session.nicknym.keymanager

    soledad_querier = SoledadQuerier(soledad=leap_session.account._soledad)

    search_engine = SearchEngine(soledad_querier, agent_home=leap_home)
    pixelated_mail_sender = MailSender(leap_session.account_email(),
                                       lambda: leap_session.smtp.ensure_running())

    pixelated_mailboxes = Mailboxes(leap_session.account, soledad_querier, search_engine)
    draft_service = DraftService(pixelated_mailboxes)
    mail_service = MailService(pixelated_mailboxes, pixelated_mail_sender, soledad_querier, search_engine)

    MailboxIndexerListener.SEARCH_ENGINE = search_engine
    InputMail.FROM_EMAIL_ADDRESS = leap_session.account_email()

    app.resource.initialize(soledad_querier, keymanager, search_engine, mail_service, draft_service)

    register(signal=proto.SOLEDAD_DONE_DATA_SYNC,
             callback=init_index_and_remove_dupes(querier=soledad_querier,
                                                  search_engine=search_engine,
                                                  mail_service=mail_service))

    register(signal=proto.SOLEDAD_DONE_DATA_SYNC,
             callback=check_welcome_mail_wrapper(pixelated_mailboxes.inbox()))

    register(signal=proto.SOLEDAD_DONE_DATA_SYNC, uid=CREATE_KEYS_IF_KEYS_DONT_EXISTS_CALLBACK,
             callback=look_for_user_key_and_create_if_cant_find(leap_session))

    reactor.threadpool.adjustPoolsize(20, 40)
    reactor.stop = stop_incoming_mail_fetcher(reactor.stop, leap_session)


def create_app(app, args, leap_session):
    app.resource = RootResource()
    init_app(app, args.home, leap_session)
    if args.sslkey and args.sslcert:
        listen_with_ssl(app, args)
    else:
        listen_without_ssl(app, args)


def listen_without_ssl(app, args):
    reactor.listenTCP(args.port, Site(app.resource), interface=args.host)


def _ssl_options(args):
    with open(args.sslkey) as keyfile:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, keyfile.read())
    with open(args.sslcert) as certfile:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, certfile.read())
    acceptable = ssl.AcceptableCiphers.fromOpenSSLCipherString(
        u'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:!RC4:HIGH:!MD5:!aNULL:!EDH')
    options = ssl.CertificateOptions(privateKey=pkey, certificate=cert, method=SSL.TLSv1_2_METHOD,
                                     acceptableCiphers=acceptable)
    return options


def listen_with_ssl(app, args):
    reactor.listenSSL(args.port, Site(app.resource), _ssl_options(args), interface=args.host)


class RedirectToSSL(resource.Resource):
    isLeaf = True

    def __init__(self, ssl_port):
        self.ssl_port = ssl_port

    def render_GET(self, request):
        host = request.getHost().host
        return redirectTo("https://%s:%s" % (host, self.ssl_port), request)
