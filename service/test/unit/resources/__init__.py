from twisted.internet.defer import succeed
from twisted.web import server
from twisted.web.server import Site


def resolve_result(request, result):
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(request)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return succeed(request)
        else:
            return request.notifyFinish().addCallback(lambda _: request)
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class DummySite(Site):

    def get(self, request):
        return resolve_result(
            request, self.getResourceFor(request).render(request))
