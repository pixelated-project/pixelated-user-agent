
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

import argparse

from mailbox import Maildir
from pixelated.config.app import App
from pixelated.config.args import parser_add_default_arguments
from pixelated.config.config_ua import config_user_agent
from pixelated.config.dispatcher import config_dispatcher
from pixelated.config.events_server import init_events_server
from pixelated.config.logging_setup import init_logging
from pixelated.config.leap_cert import init_leap_cert
from pixelated.config.soledad import init_soledad_and_user_key
from twisted.internet import reactor, defer
from twisted.internet.threads import deferToThread

from leap.mail.imap.fields import WithMsgFields
from leap.common.events import register, unregister
from leap.common.events import catalog as events

# monkey patching some specifics
import pixelated.support.ext_protobuf
import pixelated.support.ext_sqlcipher
import pixelated.support.ext_esmtp_sender_factory
import pixelated.support.ext_fetch
import pixelated.support.ext_keymanager_fetch_key
import pixelated.support.ext_requests_urllib3


def initialize():
    args = parse_args()
    app = App()

    init_logging(args)
    init_leap_cert(args)

    if args.dispatcher or args.dispatcher_stdin:
        config_dispatcher(app, args)
    else:
        config_user_agent(app, args)

    init_events_server()
    execute_command = create_execute_command(args, app)

    reactor.callWhenRunning(execute_command)
    reactor.run()


def parse_args():
    parser = argparse.ArgumentParser(description='pixelated maintenance')
    parser_add_default_arguments(parser)
    subparsers = parser.add_subparsers(help='commands', dest='command')
    subparsers.add_parser('reset', help='reset account command')
    mails_parser = subparsers.add_parser('load-mails', help='load mails into account')
    mails_parser.add_argument('file', nargs='+', help='file(s) with mail data')

    subparsers.add_parser('dump-soledad', help='dump the soledad database')
    subparsers.add_parser('sync', help='sync the soledad database')

    return parser.parse_args()


def create_execute_command(args, app):
    def execute_command():

        def init_soledad():
            return init_soledad_and_user_key(app, args.home)

        def get_soledad_handle(leap_session):
            soledad = leap_session.soledad_session.soledad

            return leap_session, soledad

        def soledad_sync(args):
            leap_session, soledad = args

            soledad.sync()

            return args

        prepare = deferToThread(init_soledad)
        prepare.addCallback(get_soledad_handle)
        prepare.addCallback(soledad_sync)

        def execute_command_callback():
            def wrapper(*_):
                d = command_callback(args)
                tearDown = defer.Deferred()
                # tearDown.addCallback(soledad_sync) Need soledad args from init_soledad
                tearDown.addCallback(shutdown)
                d.chainDeferred(tearDown)
                d.addErrback(shutdown_on_error)
                reactor.callWhenRunning(d.callback, None)
            return wrapper

        register(events.SOLEDAD_DONE_DATA_SYNC,
                 uid=1337,
                 callback=execute_command_callback())

    return execute_command


def command_callback(args):
    d = defer.Deferred()
    if args.command == 'reset':
        d.addCallback(delete_all_mails)
    elif args.command == 'load-mails':
        d.addCallback(load_mails, args.file)
    elif args.command == 'dump-soledad':
        d.addCallback(dump_soledad)
    elif args.command == 'sync':
        # nothing to do here, sync is already part of the chain
        pass
    else:
        print 'Unsupported command: %s' % args.command
    return d


def delete_all_mails(args):
    leap_session, soledad = args
    generation, docs = soledad.get_all_docs()

    for doc in docs:
        if doc.content.get('type', None) in ['head', 'cnt', 'flags']:
            soledad.delete_doc(doc)

    return args


def is_keep_file(mail):
    return mail['subject'] is None


def add_mail_folder(account, maildir, folder_name, deferreds):
    import ipdb; ipdb.set_trace()
    mailboxes_names = yield account.list_all_mailboxes()
    if folder_name not in mailboxes_names:
        account.addMailbox(folder_name)

    mbx = account.getMailbox(folder_name)
    for mail in maildir:
        if is_keep_file(mail):
            continue

        flags = (WithMsgFields.RECENT_FLAG,) if mail.get_subdir() == 'new' else ()
        if 'S' in mail.get_flags():
            flags = (WithMsgFields.SEEN_FLAG,) + flags
        if 'R' in mail.get_flags():
            flags = (WithMsgFields.ANSWERED_FLAG,) + flags

        deferreds.append(mbx.addMessage(mail.as_string(), flags=flags, notify_on_disk=False))


@defer.inlineCallbacks
def load_mails(args, mail_paths):
    leap_session, soledad = args
    account = leap_session.account

    deferreds = []

    for path in mail_paths:
        maildir = Maildir(path, factory=None)
        add_mail_folder(account, maildir, 'INBOX', deferreds)
        for mail_folder_name in maildir.list_folders():
            mail_folder = maildir.get_folder(mail_folder_name)
            add_mail_folder(account, mail_folder, mail_folder_name, deferreds)

    yield defer.DeferredList(deferreds)
    defer.returnValue(args)


def flush_to_soledad(args, finalize):
    leap_session, soledad = args
    account = leap_session.account
    memstore = account._memstore
    permanent_store = memstore._permanent_store

    d = memstore.write_messages(permanent_store)

    def check_flushed(args):
        if memstore.is_writing:
            reactor.callLater(1, check_flushed, args)
        else:
            finalize.callback((leap_session, soledad))

    d.addCallback(check_flushed)

    return args


def dump_soledad(args):
    leap_session, soledad = args

    generation, docs = soledad.get_all_docs()

    for doc in docs:
        print doc
        print '\n'

    return args


def shutdown(args):
    reactor.stop()


def shutdown_on_error(error):
    print error
    shutdown(None)

if __name__ == '__main__':
    initialize()
