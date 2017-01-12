from mock import MagicMock
from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest
from pixelated.resources.tags_resource import TagsResource
from test.unit.resources import DummySite


class TestTagsResource(unittest.TestCase):
    def setUp(self):
        self.services_factory = MagicMock()
        self.resource = TagsResource(self.services_factory)

    def test_errback_is_called(self):
        exception = Exception('')
        mock_search_engine = MagicMock()
        mock_search_engine.tags = MagicMock(side_effect=exception)
        mock_service = MagicMock()
        mock_service.search_engine = mock_search_engine
        self.services_factory.services.return_value = mock_service
        self.web = DummySite(self.resource)

        request = DummyRequest(['/tags'])
        request.method = 'GET'

        d = self.web.get(request)

        def assert_500_when_exception_is_thrown(_):
            self.assertEqual(500, request.responseCode)
            self.assertEqual('Something went wrong!', request.written[0])

        d.addCallback(assert_500_when_exception_is_thrown)
        return d
