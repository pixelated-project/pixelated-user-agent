import json
from pixelated.adapter.services.mail_sender import SMTPDownException
from pixelated.adapter.model.mail import InputMail
from pixelated.resources import respond_json, respond_json_deferred
from twisted.web.resource import Resource
from twisted.web import server
from leap.common.events import catalog as events
from leap.common.events import register


class MailsUnreadResource(Resource):
    isLeaf = True

    def __init__(self, mail_service):
        Resource.__init__(self)
        self._mail_service = mail_service

    def render_POST(self, request):
        idents = json.load(request.content).get('idents')
        for ident in idents:
            self._mail_service.mark_as_unread(ident)
        return respond_json(None, request)


class MailsReadResource(Resource):
    isLeaf = True

    def __init__(self, mail_service):
        Resource.__init__(self)
        self._mail_service = mail_service

    def render_POST(self, request):
        idents = json.load(request.content).get('idents')
        for ident in idents:
            self._mail_service.mark_as_read(ident)

        return respond_json(None, request)


class MailsDeleteResource(Resource):
    isLeaf = True

    def __init__(self, mail_service):
        Resource.__init__(self)
        self._mail_service = mail_service

    def render_POST(self, request):
        idents = json.loads(request.content.read())['idents']
        for ident in idents:
            self._mail_service.delete_mail(ident)
        return respond_json(None, request)


class MailsRecoverResource(Resource):
    isLeaf = True

    def __init__(self, mail_service):
        Resource.__init__(self)
        self._mail_service = mail_service

    def render_POST(self, request):
        idents = json.loads(request.content.read())['idents']
        for ident in idents:
            self._mail_service.recover_mail(ident)
        return respond_json(None, request)


class MailsResource(Resource):

    def _register_smtp_error_handler(self):

        def on_error(event):
            delivery_error_mail = InputMail.delivery_error_template(delivery_address=event.content)
            self._mail_service.mailboxes.inbox().add(delivery_error_mail)

        register(events.SMTP_SEND_MESSAGE_ERROR, callback=on_error)

    def __init__(self, mail_service, draft_service):
        Resource.__init__(self)
        self.putChild('delete', MailsDeleteResource(mail_service))
        self.putChild('recover', MailsRecoverResource(mail_service))
        self.putChild('read', MailsReadResource(mail_service))
        self.putChild('unread', MailsUnreadResource(mail_service))

        self._draft_service = draft_service
        self._mail_service = mail_service
        self._register_smtp_error_handler()

    def render_GET(self, request):
        query, window_size, page = request.args.get('q')[0], request.args.get('w')[0], request.args.get('p')[0]
        mails, total = self._mail_service.mails(query, window_size, page)

        response = {
            "stats": {
                "total": total,
            },
            "mails": [mail.as_dict() for mail in mails]
        }

        return respond_json(response, request)

    def render_POST(self, request):
        content_dict = json.loads(request.content.read())

        deferred = self._mail_service.send_mail(content_dict)

        def onSuccess(sent_mail):
            data = sent_mail.as_dict()
            respond_json_deferred(data, request)

        def onError(error):
            if isinstance(error.value, SMTPDownException):
                respond_json_deferred({'message': str(error.value)}, request, status_code=503)
            else:
                respond_json_deferred({'message': str(error)}, request, status_code=422)

        deferred.addCallback(onSuccess)
        deferred.addErrback(onError)

        return server.NOT_DONE_YET

    def render_PUT(self, request):
        content_dict = json.loads(request.content.read())
        _mail = InputMail.from_dict(content_dict)
        draft_id = content_dict.get('ident')

        if draft_id:
            if not self._mail_service.mail_exists(draft_id):
                return respond_json("", request, status_code=422)
            pixelated_mail = self._draft_service.update_draft(draft_id, _mail)
        else:
            pixelated_mail = self._draft_service.create_draft(_mail)

        return respond_json({'ident': pixelated_mail.ident}, request)
